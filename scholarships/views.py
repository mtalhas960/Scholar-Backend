from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models import Count
from .models import Scholarship, StudyLevel, FundingType, Country, FieldOfStudy
from .serializers import ScholarshipSerializer
from .pagination import StandardResultsPagination
from .recommendation import StudentProfile, ScholarshipStub, rank_scholarships


class ScholarshipViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve scholarships. Public — no auth required."""
    queryset = Scholarship.objects.select_related('country', 'degree_level', 'field_of_study', 'funding_type').all()
    serializer_class = ScholarshipSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'eligibility_criteria']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        # Filter by degree_level name(s)
        levels = params.getlist('degree_level')
        if levels:
            qs = qs.filter(degree_level__name__in=levels)

        # Filter by funding_type name(s)
        fundings = params.getlist('funding_type')
        if fundings:
            qs = qs.filter(funding_type__name__in=fundings)

        # Filter by country name(s)
        countries = params.getlist('country')
        if countries:
            qs = qs.filter(country__name__in=countries)

        # Filter by field_of_study name(s)
        fields = params.getlist('field_of_study')
        if fields:
            qs = qs.filter(field_of_study__name__in=fields)

        return qs

    def get_object(self):
        """Support lookup by slug or id."""
        lookup_value = self.kwargs.get('pk', '')
        try:
            int(lookup_value)
            return super().get_object()
        except (ValueError, TypeError, Scholarship.DoesNotExist):
            pass
        try:
            return Scholarship.objects.select_related(
                'country', 'degree_level', 'field_of_study', 'funding_type'
            ).get(slug=lookup_value)
        except Scholarship.DoesNotExist:
            raise NotFound('Scholarship not found')


@api_view(['GET'])
@permission_classes([AllowAny])
def taxonomy_options(request):
    """Return all taxonomy options with scholarship counts."""
    study_levels = StudyLevel.objects.annotate(
        count=Count('scholarships')
    ).order_by('order', 'name').values('id', 'name', 'slug', 'count')

    funding_types = FundingType.objects.annotate(
        count=Count('scholarships')
    ).order_by('order', 'name').values('id', 'name', 'slug', 'count')

    countries = Country.objects.annotate(
        count=Count('scholarships')
    ).order_by('order', 'name').values('id', 'name', 'slug', 'flag', 'code', 'count')

    fields = FieldOfStudy.objects.annotate(
        count=Count('scholarships')
    ).order_by('order', 'name').values('id', 'name', 'slug', 'count')

    return Response({
        'study_levels': list(study_levels),
        'funding_types': list(funding_types),
        'countries': list(countries),
        'fields_of_study': list(fields),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations_view(request):
    """
    Return scholarships ranked by how well they match the
    authenticated student's profile.
    """
    from accounts.models import Profile

    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Build student profile
    student = StudentProfile(
        degree_level=profile.degree_level or "",
        field_of_study_names=frozenset(
            profile.field_of_study.values_list("name", flat=True)
        ),
        preferred_country_names=frozenset(
            profile.preferred_countries.values_list("name", flat=True)
        ),
        funding_pref_names=frozenset(
            profile.funding_preferences.values_list("name", flat=True)
        ),
    )

    # Fetch all scholarships as stubs
    scholarships = [
        ScholarshipStub(
            id=s.id,
            degree_level_name=s.degree_level.name,
            field_of_study_name=s.field_of_study.name,
            funding_type_name=s.funding_type.name,
            country_name=s.country.name,
        )
        for s in Scholarship.objects.select_related(
            'degree_level', 'field_of_study', 'funding_type', 'country'
        ).all()
    ]

    # Score and rank
    ranked = rank_scholarships(student, scholarships)

    # Map IDs → full serialized data
    id_to_scholarship = {
        s.id: s
        for s in Scholarship.objects.select_related(
            'country', 'degree_level', 'field_of_study', 'funding_type'
        ).all()
    }
    serializer = ScholarshipSerializer(
        [id_to_scholarship[r.scholarship_id] for r in ranked if r.scholarship_id in id_to_scholarship],
        many=True,
    )

    # Attach scores to serialized data
    score_map = {r.scholarship_id: r.total for r in ranked}
    results = []
    for item in serializer.data:
        item["match_score"] = score_map.get(item["id"], 0)
        results.append(item)

    return Response(results)
