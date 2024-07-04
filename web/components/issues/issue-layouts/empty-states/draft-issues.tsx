import { observer } from "mobx-react-lite";
import { useRouter } from "next/router";
import size from "lodash/size";
// hooks
import { useIssues, useUser } from "hooks/store";
// components
import { EmptyState, getEmptyStateImagePath } from "components/empty-state";
// constants
import { EUserProjectRoles } from "constants/project";
import { EIssueFilterType, EIssuesStoreType } from "constants/issue";
// types
import { IIssueFilterOptions } from "@plane/types";

interface EmptyStateProps {
  title: string;
  image: string;
  description?: string;
  comicBox?: { title: string; description: string };
  primaryButton?: { text: string; icon?: React.ReactNode; onClick: () => void };
  secondaryButton?: { text: string; onClick: () => void };
  size?: "lg" | "sm" | undefined;
  disabled?: boolean | undefined;
}

export const ProjectDraftEmptyState: React.FC = observer(() => {
  // router
  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;
  const {
    membership: { currentProjectRole },
    currentUser,
  } = useUser();
  const { issuesFilter } = useIssues(EIssuesStoreType.DRAFT);

  const userFilters = issuesFilter?.issueFilters?.filters;
  const activeLayout = issuesFilter?.issueFilters?.displayFilters?.layout;

  const currentLayoutEmptyStateImagePath = getEmptyStateImagePath(
    "empty-filters",
    activeLayout ?? "list",
    currentUser?.theme.theme === "light"
  );
  const EmptyStateImagePath = getEmptyStateImagePath("draft", "empty-issues", currentUser?.theme.theme === "light");

  const issueFilterCount = size(
    Object.fromEntries(
      Object.entries(userFilters ?? {}).filter(([key, value]) => value && Array.isArray(value) && value.length > 0)
    )
  );

  const handleClearAllFilters = () => {
    if (!workspaceSlug || !projectId) return;
    const newFilters: IIssueFilterOptions = {};
    Object.keys(userFilters ?? {}).forEach((key) => {
      newFilters[key as keyof IIssueFilterOptions] = null;
    });
    issuesFilter.updateFilters(workspaceSlug.toString(), projectId.toString(), EIssueFilterType.FILTERS, {
      ...newFilters,
    });
  };

  const isEditingAllowed = !!currentProjectRole && currentProjectRole >= EUserProjectRoles.MEMBER;

  const emptyStateProps: EmptyStateProps =
    issueFilterCount > 0
      ? {
          title: "No issues found matching the filters applied",
          image: currentLayoutEmptyStateImagePath,
          secondaryButton: {
            text: "Clear all filters",
            onClick: handleClearAllFilters,
          },
        }
      : {
          title: "No draft issues yet",
          description:
            "Quickly stepping away but want to keep your place? No worries – save a draft now. Your issues will be right here waiting for you.",
          image: EmptyStateImagePath,
          size: "sm",
          disabled: !isEditingAllowed,
        };

  return (
    <div className="relative h-full w-full overflow-y-auto">
      <EmptyState {...emptyStateProps} />
    </div>
  );
});
