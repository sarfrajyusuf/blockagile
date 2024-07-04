import { Controller, useForm } from "react-hook-form";
// components
import { DateDropdown, ProjectDropdown } from "components/dropdowns";
// ui
import { Button, Input, TextArea } from "@plane/ui";
// helpers
import { renderFormattedPayloadDate } from "helpers/date-time.helper";
// types
import { ICycle } from "@plane/types";

type Props = {
  handleFormSubmit: (values: Partial<ICycle>) => Promise<void>;
  handleClose: () => void;
  projectId: string;
  setActiveProject: (projectId: string) => void;
  data?: ICycle | null;
};

export const CycleEndForm: React.FC<Props> = (props) => {
  const { handleFormSubmit, handleClose, projectId, setActiveProject, data } = props;
  // form data
  const timeNow = renderFormattedPayloadDate(new Date());
  const {
    formState: { errors, isSubmitting },
    handleSubmit,
    control,
    watch,
  } = useForm<ICycle>({
    defaultValues: {
      project: projectId,
      name: data?.name || "",
      description: data?.description || "",
      start_date: data?.start_date || null,
      end_date: timeNow,
    },
  });

  const startDate = watch("start_date");
  const endDate = watch("end_date");

  const minDate = startDate ? new Date(startDate) : new Date();
  minDate.setDate(minDate.getDate() + 1);

  const maxDate = endDate ? new Date(endDate) : null;
  maxDate?.setDate(maxDate.getDate() - 1);

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div className="space-y-5">
        <div className="flex items-center gap-x-3">
          {!status && (
            <Controller
              control={control}
              name="project"
              render={({ field: { value, onChange } }) => (
                <ProjectDropdown
                  value={value}
                  onChange={(val) => {
                    onChange(val);
                    setActiveProject(val);
                  }}
                  buttonVariant="background-with-text"
                  tabIndex={7}
                />
              )}
            />
          )}
          <h3 className="text-xl font-medium leading-6 text-custom-text-200">{status ? "Update" : "New"} Sprint</h3>
        </div>
        <div className="space-y-3">
          <div className="mt-2 space-y-3">
            <h2>Do you want to end this sprint?</h2>
            <div className="flex flex-wrap items-center gap-2">
              <div>
                <Controller
                  control={control}
                  name="start_date"
                  render={({ field: { value, onChange } }) => (
                    <div className="h-7">
                      <DateDropdown
                        value={value}
                        onChange={(date) => onChange(date ? renderFormattedPayloadDate(date) : null)}
                        buttonVariant="border-with-text"
                        placeholder="Start date"
                        minDate={new Date()}
                        maxDate={maxDate ?? undefined}
                        tabIndex={3}
                      />
                    </div>
                  )}
                />
              </div>
              <Controller
                control={control}
                name="end_date"
                render={({ field: { value, onChange } }) => (
                  <div className="h-7">
                    <DateDropdown
                      value={value}
                      onChange={(date) => onChange(date ? renderFormattedPayloadDate(date) : null)}
                      buttonVariant="border-with-text"
                      placeholder="End date"
                      minDate={minDate}
                      tabIndex={4}
                    />
                  </div>
                )}
              />
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-end gap-2 border-t-[0.5px] border-custom-border-100 pt-5 ">
        <Button variant="neutral-primary" size="sm" onClick={handleClose} tabIndex={5}>
          Cancel
        </Button>
        <Button variant="primary" size="sm" type="submit" loading={isSubmitting} tabIndex={6}>
          {(isSubmitting ? "Ending" : "End sprint") }
        </Button>
      </div>
    </form>
  );
};
