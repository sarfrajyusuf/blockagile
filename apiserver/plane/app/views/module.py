# Python imports
import json

# Django Imports
from django.utils import timezone
from django.db.models import Prefetch, F, OuterRef, Func, Exists, Count, Q
from django.core import serializers
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page

# Third party imports
from rest_framework.response import Response
from rest_framework import status

# Module imports
from . import BaseViewSet, BaseAPIView, WebhookMixin
from plane.app.serializers import (
    ModuleWriteSerializer,
    ModuleSerializer,
    ModuleIssueSerializer,
    ModuleLinkSerializer,
    ModuleFavoriteSerializer,
    IssueSerializer,
    ModuleUserPropertiesSerializer,
)
from plane.app.permissions import (
    ProjectEntityPermission,
    ProjectLitePermission,
)
from plane.db.models import (
    Module,
    ModuleIssue,
    Project,
    Issue,
    ModuleLink,
    ModuleFavorite,
    IssueLink,
    IssueAttachment,
    IssueSubscriber,
    ModuleUserProperties,
)
from plane.bgtasks.issue_activites_task import issue_activity
from plane.utils.grouper import group_results
from plane.utils.issue_filters import issue_filters
from plane.utils.analytics_plot import burndown_plot


class ModuleViewSet(WebhookMixin, BaseViewSet):
    model = Module
    permission_classes = [
        ProjectEntityPermission,
    ]
    webhook_event = "module"

    def get_serializer_class(self):
        return (
            ModuleWriteSerializer
            if self.action in ["create", "update", "partial_update"]
            else ModuleSerializer
        )

    def get_queryset(self):
        print("in get query module ",self.request.user)
        print("KWAysnfr ",self.kwargs.get("project_id")," testinsf ",self.kwargs.get("slug"),OuterRef("pk"))
        testquery =ModuleFavorite.objects.filter(
            user=self.request.user,
            project_id=self.kwargs.get("project_id"),
            workspace__slug=self.kwargs.get("slug"),
        )
        print("trisf ",OuterRef("pk"))
        print("Test Qeudidr ",testquery)
        
        subquery = ModuleFavorite.objects.filter(
            user=self.request.user,
            module_id=OuterRef("pk"),
            project_id=self.kwargs.get("project_id"),
            workspace__slug=self.kwargs.get("slug"),
        )
         

        
        return (
            super()
            .get_queryset()
            .filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .annotate(is_favorite=Exists(subquery))
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .prefetch_related("members")
            .prefetch_related(
                Prefetch(
                    "link_module",
                    queryset=ModuleLink.objects.select_related(
                        "module", "created_by"
                    ),
                )
            )
            .annotate(
                total_issues=Count(
                    "issue_module",
                    filter=Q(
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                ),
            )
            .annotate(
                completed_issues=Count(
                    "issue_module__issue__state__group",
                    filter=Q(
                        issue_module__issue__state__group="completed",
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                )
            )
            .annotate(
                cancelled_issues=Count(
                    "issue_module__issue__state__group",
                    filter=Q(
                        issue_module__issue__state__group="cancelled",
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                )
            )
            .annotate(
                started_issues=Count(
                    "issue_module__issue__state__group",
                    filter=Q(
                        issue_module__issue__state__group="started",
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                )
            )
            .annotate(
                unstarted_issues=Count(
                    "issue_module__issue__state__group",
                    filter=Q(
                        issue_module__issue__state__group="unstarted",
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                )
            )
            .annotate(
                backlog_issues=Count(
                    "issue_module__issue__state__group",
                    filter=Q(
                        issue_module__issue__state__group="backlog",
                        issue_module__issue__archived_at__isnull=True,
                        issue_module__issue__is_draft=False,
                    ),
                )
            )
            .order_by("-is_favorite", "-created_at")
        )

    def create(self, request, slug, project_id):
        print("Testing in create module")
        project = Project.objects.get(workspace__slug=slug, pk=project_id)
        serializer = ModuleWriteSerializer(
            data=request.data, context={"project": project}
        )
        print("serializer in create module",serializer)
        if serializer.is_valid():
            serializer.save()
            module = Module.objects.get(pk=serializer.data["id"])
            serializer = ModuleSerializer(module)
            print("if dsave in create module",serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("error in create module")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, slug, project_id):
        print("in list ")
        queryset = self.get_queryset()
        print("queryset in list module")
        fields = [
            field
            for field in request.GET.get("fields", "").split(",")
            if field
        ]
        print("fields in module ",fields)
        modules = ModuleSerializer(
            queryset, many=True, fields=fields if fields else None
        ).data
        return Response(modules, status=status.HTTP_200_OK)

    def retrieve(self, request, slug, project_id, pk):
        print("in retireive module")
        queryset = self.get_queryset().get(pk=pk)
        print("retrieve queryset")
        assignee_distribution = (
            Issue.objects.filter(
                issue_module__module_id=pk,
                workspace__slug=slug,
                project_id=project_id,
            )
            .annotate(first_name=F("assignees__first_name"))
            .annotate(last_name=F("assignees__last_name"))
            .annotate(assignee_id=F("assignees__id"))
            .annotate(display_name=F("assignees__display_name"))
            .annotate(avatar=F("assignees__avatar"))
            .values(
                "first_name",
                "last_name",
                "assignee_id",
                "avatar",
                "display_name",
            )
            .annotate(
                total_issues=Count(
                    "assignee_id",
                    filter=Q(
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
            )
            .annotate(
                completed_issues=Count(
                    "assignee_id",
                    filter=Q(
                        completed_at__isnull=False,
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
            )
            .annotate(
                pending_issues=Count(
                    "assignee_id",
                    filter=Q(
                        completed_at__isnull=True,
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
            )
            .order_by("first_name", "last_name")
        )
        print("assignee_distribution ")
        label_distribution = (
            Issue.objects.filter(
                issue_module__module_id=pk,
                workspace__slug=slug,
                project_id=project_id,
            )
            .annotate(label_name=F("labels__name"))
            .annotate(color=F("labels__color"))
            .annotate(label_id=F("labels__id"))
            .values("label_name", "color", "label_id")
            .annotate(
                total_issues=Count(
                    "label_id",
                    filter=Q(
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                ),
            )
            .annotate(
                completed_issues=Count(
                    "label_id",
                    filter=Q(
                        completed_at__isnull=False,
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
            )
            .annotate(
                pending_issues=Count(
                    "label_id",
                    filter=Q(
                        completed_at__isnull=True,
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
            )
            .order_by("label_name")
        )
        print("label_distribution ")

        data = ModuleSerializer(queryset).data
        data["distribution"] = {
            "assignees": assignee_distribution,
            "labels": label_distribution,
            "completion_chart": {},
        }
        print("data in retire ufv s ",data)

        if queryset.start_date and queryset.target_date:
            print("in if querysbejt ",queryset)
            data["distribution"]["completion_chart"] = burndown_plot(
                queryset=queryset,
                slug=slug,
                project_id=project_id,
                module_id=pk,
            )
        print("in retirenvie ns ",data)
        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, slug, project_id, pk):
        module = Module.objects.get(
            workspace__slug=slug, project_id=project_id, pk=pk
        )
        module_issues = list(
            ModuleIssue.objects.filter(module_id=pk).values_list(
                "issue", flat=True
            )
        )
        issue_activity.delay(
            type="module.activity.deleted",
            requested_data=json.dumps(
                {
                    "module_id": str(pk),
                    "module_name": str(module.name),
                    "issues": [str(issue_id) for issue_id in module_issues],
                }
            ),
            actor_id=str(request.user.id),
            issue_id=str(pk),
            project_id=str(project_id),
            current_instance=None,
            epoch=int(timezone.now().timestamp()),
            notification=True,
            origin=request.META.get("HTTP_ORIGIN"),
        )
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ModuleIssueViewSet(WebhookMixin, BaseViewSet):
    serializer_class = ModuleIssueSerializer
    model = ModuleIssue
    webhook_event = "module_issue"
    bulk = True

    filterset_fields = [
        "issue__labels__id",
        "issue__assignees__id",
    ]

    permission_classes = [
        ProjectEntityPermission,
    ]

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(
                    parent=OuterRef("issue")
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(project_id=self.kwargs.get("project_id"))
            .filter(module_id=self.kwargs.get("module_id"))
            .filter(project__project_projectmember__member=self.request.user)
            .select_related("project")
            .select_related("workspace")
            .select_related("module")
            .select_related("issue", "issue__state", "issue__project")
            .prefetch_related("issue__assignees", "issue__labels")
            .prefetch_related("module__members")
            .distinct()
        )

    @method_decorator(gzip_page)
    def list(self, request, slug, project_id, module_id):
        fields = [
            field
            for field in request.GET.get("fields", "").split(",")
            if field
        ]
        order_by = request.GET.get("order_by", "created_at")
        filters = issue_filters(request.query_params, "GET")
        issues = (
            Issue.issue_objects.filter(issue_module__module_id=module_id)
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(
                    parent=OuterRef("id")
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .filter(project_id=project_id)
            .filter(workspace__slug=slug)
            .select_related("project")
            .select_related("workspace")
            .select_related("state")
            .select_related("parent")
            .prefetch_related("assignees")
            .prefetch_related("labels")
            .order_by(order_by)
            .filter(**filters)
            .annotate(cycle_id=F("issue_cycle__cycle_id"))
            .annotate(module_id=F("issue_module__module_id"))
            .annotate(
                link_count=IssueLink.objects.filter(issue=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                attachment_count=IssueAttachment.objects.filter(
                    issue=OuterRef("id")
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                is_subscribed=Exists(
                    IssueSubscriber.objects.filter(
                        subscriber=self.request.user, issue_id=OuterRef("id")
                    )
                )
            )
        )
        serializer = IssueSerializer(
            issues, many=True, fields=fields if fields else None
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, slug, project_id, module_id):
        issues = request.data.get("issues", [])
        if not len(issues):
            return Response(
                {"error": "Issues are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        module = Module.objects.get(
            workspace__slug=slug, project_id=project_id, pk=module_id
        )

        module_issues = list(ModuleIssue.objects.filter(issue_id__in=issues))

        update_module_issue_activity = []
        records_to_update = []
        record_to_create = []

        for issue in issues:
            module_issue = [
                module_issue
                for module_issue in module_issues
                if str(module_issue.issue_id) in issues
            ]

            if len(module_issue):
                if module_issue[0].module_id != module_id:
                    update_module_issue_activity.append(
                        {
                            "old_module_id": str(module_issue[0].module_id),
                            "new_module_id": str(module_id),
                            "issue_id": str(module_issue[0].issue_id),
                        }
                    )
                    module_issue[0].module_id = module_id
                    records_to_update.append(module_issue[0])
            else:
                record_to_create.append(
                    ModuleIssue(
                        module=module,
                        issue_id=issue,
                        project_id=project_id,
                        workspace=module.workspace,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                )

        ModuleIssue.objects.bulk_create(
            record_to_create,
            batch_size=10,
            ignore_conflicts=True,
        )

        ModuleIssue.objects.bulk_update(
            records_to_update,
            ["module"],
            batch_size=10,
        )

        # Capture Issue Activity
        issue_activity.delay(
            type="module.activity.created",
            requested_data=json.dumps({"modules_list": issues}),
            actor_id=str(self.request.user.id),
            issue_id=None,
            project_id=str(self.kwargs.get("project_id", None)),
            current_instance=json.dumps(
                {
                    "updated_module_issues": update_module_issue_activity,
                    "created_module_issues": serializers.serialize(
                        "json", record_to_create
                    ),
                }
            ),
            epoch=int(timezone.now().timestamp()),
            notification=True,
            origin=request.META.get("HTTP_ORIGIN"),
        )

        issues = self.get_queryset().values_list("issue_id", flat=True)

        return Response(
            IssueSerializer(
                Issue.objects.filter(pk__in=issues), many=True
            ).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, slug, project_id, module_id, issue_id):
        module_issue = ModuleIssue.objects.get(
            workspace__slug=slug,
            project_id=project_id,
            module_id=module_id,
            issue_id=issue_id,
        )
        issue_activity.delay(
            type="module.activity.deleted",
            requested_data=json.dumps(
                {
                    "module_id": str(module_id),
                    "issues": [str(issue_id)],
                }
            ),
            actor_id=str(request.user.id),
            issue_id=str(issue_id),
            project_id=str(project_id),
            current_instance=None,
            epoch=int(timezone.now().timestamp()),
            notification=True,
            origin=request.META.get("HTTP_ORIGIN"),
        )
        module_issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ModuleLinkViewSet(BaseViewSet):
    permission_classes = [
        ProjectEntityPermission,
    ]

    model = ModuleLink
    serializer_class = ModuleLinkSerializer

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs.get("project_id"),
            module_id=self.kwargs.get("module_id"),
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(project_id=self.kwargs.get("project_id"))
            .filter(module_id=self.kwargs.get("module_id"))
            .filter(project__project_projectmember__member=self.request.user)
            .order_by("-created_at")
            .distinct()
        )


class ModuleFavoriteViewSet(BaseViewSet):
    serializer_class = ModuleFavoriteSerializer
    model = ModuleFavorite

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(user=self.request.user)
            .select_related("module")
        )

    def create(self, request, slug, project_id):
        serializer = ModuleFavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug, project_id, module_id):
        module_favorite = ModuleFavorite.objects.get(
            project=project_id,
            user=request.user,
            workspace__slug=slug,
            module_id=module_id,
        )
        module_favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ModuleUserPropertiesEndpoint(BaseAPIView):
    permission_classes = [
        ProjectLitePermission,
    ]

    def patch(self, request, slug, project_id, module_id):
        module_properties = ModuleUserProperties.objects.get(
            user=request.user,
            module_id=module_id,
            project_id=project_id,
            workspace__slug=slug,
        )

        module_properties.filters = request.data.get(
            "filters", module_properties.filters
        )
        module_properties.display_filters = request.data.get(
            "display_filters", module_properties.display_filters
        )
        module_properties.display_properties = request.data.get(
            "display_properties", module_properties.display_properties
        )
        module_properties.save()

        serializer = ModuleUserPropertiesSerializer(module_properties)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug, project_id, module_id):
        module_properties, _ = ModuleUserProperties.objects.get_or_create(
            user=request.user,
            project_id=project_id,
            module_id=module_id,
            workspace__slug=slug,
        )
        serializer = ModuleUserPropertiesSerializer(module_properties)
        return Response(serializer.data, status=status.HTTP_200_OK)
