import {
  GanttChartSquare,
  LayoutGrid,
  List,
  AlertOctagon,
  BarChart4,
  CircleDashed,
  Folder,
  Microscope,
  Search,
} from "lucide-react";

// types
import { TCycleLayout, TCycleView } from "@plane/types";

export const CYCLE_TAB_LIST: {
  key: TCycleView;
  name: string;
}[] = [
  {
    key: "all",
    name: "All",
  },
  {
    key: "active",
    name: "Active",
  },
  {
    key: "upcoming",
    name: "Upcoming",
  },
  {
    key: "completed",
    name: "Completed",
  },
  {
    key: "draft",
    name: "Drafts",
  },
];

export const CYCLE_VIEW_LAYOUTS: {
  key: TCycleLayout;
  icon: any;
  title: string;
}[] = [
  {
    key: "list",
    icon: List,
    title: "List layout",
  },
  {
    key: "board",
    icon: LayoutGrid,
    title: "Grid layout",
  },
  {
    key: "gantt",
    icon: GanttChartSquare,
    title: "Gantt layout",
  },
];

export const CYCLE_STATUS: {
  label: string;
  value: "current" | "upcoming" | "completed" | "draft";
  color: string;
  textColor: string;
  bgColor: string;
}[] = [
  {
    label: "day left",
    value: "current",
    color: "#F59E0B",
    textColor: "text-amber-500",
    bgColor: "bg-amber-50",
  },
  {
    label: "Yet to start",
    value: "upcoming",
    color: "#3F76FF",
    textColor: "text-blue-500",
    bgColor: "bg-indigo-50",
  },
  {
    label: "Completed",
    value: "completed",
    color: "#16A34A",
    textColor: "text-green-600",
    bgColor: "bg-green-50",
  },
  {
    label: "Draft",
    value: "draft",
    color: "#525252",
    textColor: "text-custom-text-300",
    bgColor: "bg-custom-background-90",
  },
];

export const CYCLE_STATE_GROUPS_DETAILS = [
  {
    key: "backlog_issues",
    title: "Backlog",
    color: "#F0F0F3",
  },
  {
    key: "unstarted_issues",
    title: "Unstarted",
    color: "#FB923C",
  },
  {
    key: "started_issues",
    title: "Started",
    color: "#FFC53D",
  },
  {
    key: "completed_issues",
    title: "Completed",
    color: "#d687ff",
  },
  {
    key: "cancelled_issues",
    title: "Cancelled",
    color: "#ef4444",
  },
];

export const WORKSPACE_ACTIVE_CYCLES_DETAILS = [
  {
    title: "10,000-feet view of all active sprints.",
    description:
      "Zoom out to see running sprints across all your projects at once instead of going from Sprint to Sprint in each project.",
    icon: Folder,
  },
  {
    title: "Get a snapshot of each active sprint.",
    description:
      "Track high-level metrics for all active sprints, see their state of progress, and get a sense of scope against deadlines.",
    icon: CircleDashed,
  },
  {
    title: "Compare burndowns.",
    description: "Monitor how each of your teams are performing with a peek into each sprint's burndown report.",
    icon: BarChart4,
  },
  {
    title: "Quickly see make-or-break issues. ",
    description:
      "Preview high-priority issues for each sprint against due dates. See all of them per sprint in one click.",
    icon: AlertOctagon,
  },
  {
    title: "Zoom into sprints that need attention. ",
    description: "Investigate the state of any sprint that doesn’t conform to expectations in one click.",
    icon: Search,
  },
  {
    title: "Stay ahead of blockers.",
    description:
      "Spot challenges from one project to another and see inter-sprint dependencies that aren’t obvious from any other view.",
    icon: Microscope,
  },
];

export const CYCLE_EMPTY_STATE_DETAILS = {
  active: {
    key: "active",
    title: "No active sprints",
    description:
      "An active sprint includes any period that encompasses today's date within its range. Find the progress and details of the active sprint here.",
  },
  upcoming: {
    key: "upcoming",
    title: "No upcoming sprints",
    description: "Upcoming sprints on deck! Just add dates to sprints in draft, and they'll show up right here.",
  },
  completed: {
    key: "completed",
    title: "No completed cycles",
    description: "Any sprint with a past due date is considered completed. Explore all completed sprints here.",
  },
  draft: {
    key: "draft",
    title: "No draft sprints",
    description: "No dates added in sprints? Find them here as drafts.",
  },
};
