import React, { Fragment, ReactElement } from "react";
import { observer } from "mobx-react-lite";
import { Tab } from "@headlessui/react";
// hooks
import { useApplication, useProject, useUser } from "hooks/store";
// layouts
import { AppLayout } from "layouts/app-layout";
// components
import { CustomAnalytics, ScopeAndDemand } from "components/analytics";
import { WorkspaceAnalyticsHeader } from "components/headers";
import { EmptyState, getEmptyStateImagePath } from "components/empty-state";
// constants
import { ANALYTICS_TABS } from "constants/analytics";
import { EUserWorkspaceRoles } from "constants/workspace";
// type
import { NextPageWithLayout } from "lib/types";
import { PieAnalytics } from "components/analytics/scope-and-demand/pie-analytics";

const AnalyticsPage: NextPageWithLayout = observer(() => {
  // store hooks
  const {
    commandPalette: { toggleCreateProjectModal },
    eventTracker: { setTrackElement },
  } = useApplication();
  const {
    membership: { currentWorkspaceRole },
    currentUser,
  } = useUser();
  const { workspaceProjectIds } = useProject();

  const EmptyStateImagePath = getEmptyStateImagePath("onboarding", "analytics", currentUser?.theme.theme === "light");
  const isEditingAllowed = !!currentWorkspaceRole && currentWorkspaceRole >= EUserWorkspaceRoles.VIEWER;

  return (
    <>
      {workspaceProjectIds && workspaceProjectIds.length > 0 ? (
        <div className="flex h-full flex-col overflow-hidden bg-custom-background-100">
          <Tab.Group as={Fragment}>
            <Tab.List as="div" className="space-x-2 border-b border-custom-border-200 px-5 py-3">
              {ANALYTICS_TABS.map((tab) => (
                <Tab
                  key={tab.key}
                  className={({ selected }) =>
                    `rounded-3xl border border-custom-border-200 px-4 py-2 text-xs hover:bg-custom-background-80 ${
                      selected ? "bg-custom-background-80" : ""
                    }`
                  }
                  onClick={() => {}}
                >
                  {tab.title}
                </Tab>
              ))}
            </Tab.List>
            <Tab.Panels as={Fragment}>
              <Tab.Panel as={Fragment}>
                <ScopeAndDemand fullScreen />
              </Tab.Panel>
              <Tab.Panel as={Fragment}>
                <CustomAnalytics fullScreen />
              </Tab.Panel>
              <Tab.Panel as={Fragment}>
                <PieAnalytics fullScreen />
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      ) : (
        <EmptyState
          image={EmptyStateImagePath}
          title="Track progress, workloads, and allocations. Spot trends, remove blockers, and move work faster"
          description="See scope versus demand, estimates, and scope creep. Get performance by team members and teams, and make sure your project runs on time."
          primaryButton={{
            text: "Create Sprints and Modules first",
            onClick: () => {
              setTrackElement("ANALYTICS_EMPTY_STATE");
              toggleCreateProjectModal(true);
            },
          }}
          comicBox={{
            title: "Analytics works best with Sprints + Modules",
            description:
              "First, timebox your issues into Sprints and, if you can, group issues that span more than a sprint into Modules. Check out both on the left nav.",
          }}
          size="lg"
          disabled={!isEditingAllowed}
        />
      )}
    </>
  );
});

AnalyticsPage.getLayout = function getLayout(page: ReactElement) {
  return <AppLayout header={<WorkspaceAnalyticsHeader />}>{page}</AppLayout>;
};

export default AnalyticsPage;
