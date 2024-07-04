// ui
import { BarGraph, ProfileEmptyState ,PieGraph} from "components/ui";
// image
import emptyBarGraph from "public/empty-state/empty_bar_graph.svg";
// types
import { IDefaultAnalyticsResponse } from "@plane/types";
type Props = {
  defaultAnalytics: IDefaultAnalyticsResponse;
};
const getRandomLightColor = () => {
  // Generate random values for red, green, and blue components
  const red = Math.floor(Math.random() * 150) + 100; // Adjust the range for your preference
  const green = Math.floor(Math.random() * 150) + 100;
  const blue = Math.floor(Math.random() * 150) + 100;

  // Convert the components to a CSS color string
  return `rgb(${red}, ${green}, ${blue})`;
};

export const AnalyticsScopePie: React.FC<Props> = ({ defaultAnalytics }) => (
    <div className="rounded-[10px] border border-custom-border-200">
    <h5 className="p-3 text-xs text-green-500">SCOPE</h5>
    <div className="divide-y divide-custom-border-200">
      <div>
        <h6 className="px-3 text-base font-medium">Pending issues</h6>
        {defaultAnalytics.pending_issue_user && defaultAnalytics.pending_issue_user.length > 0 ? (
          <PieGraph
                data={
                  defaultAnalytics.pending_issue_user.map((group) => ({
                    id: group.assignees__id,
                    label: group.assignees__display_name,
                    value: group.count,
                    color: getRandomLightColor(),
                  })) ?? []
                }
                height="250px"
                innerRadius={0.6}
                cornerRadius={5}
                padAngle={2}
                enableArcLabels
                arcLabelsTextColor="#000000"
                enableArcLinkLabels={false}
                activeInnerRadiusOffset={5}
                colors={(datum) => datum.data.color}
                tooltip={(datum) => {
                  const assignee = defaultAnalytics.pending_issue_user.find(
                          (a) => a.assignees__id === `${datum.datum.id}`
                        );
                  return (<div className="flex items-center gap-2 rounded-md border border-custom-border-200 bg-custom-background-90 p-2 text-xs">
                    <span className="capitalize text-custom-text-200">{assignee ? assignee.assignees__display_name : "No assignee"}:{" "}</span>{" "}
                    {datum.datum.value}
                  </div>
                );
              }}
                margin={{
                  top: 32,
                  right: 0,
                  bottom: 32,
                  left: 0,
                }}
              />
        ) : (
          <div className="px-7 py-4">
            <ProfileEmptyState
              title="No Data yet"
              description="Analysis of pending issues by co-workers appears here."
              image={emptyBarGraph}
            />
          </div>
        )}
      </div>
    </div>
  </div>
);
