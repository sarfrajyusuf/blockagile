import { useEffect } from "react";
import { observer } from "mobx-react-lite";
import Image from "next/image";
// hooks
import { useApplication, useUser } from "hooks/store";
import useSignInRedirection from "hooks/use-sign-in-redirection";
// components
import { SignInRoot } from "components/account";
// ui
import { Spinner } from "@plane/ui";
// images
import BluePlaneLogoWithoutText from "public/plane-logos/blue-without-text.png";

export type AuthType = "sign-in" | "sign-up";

export const SignInView = observer(() => {
  // store hooks
  const {
    config: { envConfig },
  } = useApplication();
  const { currentUser } = useUser();
  // sign in redirection hook
  const { isRedirecting, handleRedirection } = useSignInRedirection();

  useEffect(() => {
    handleRedirection();
  }, [handleRedirection]);

  if (isRedirecting || currentUser || !envConfig)
    return (
      <div className="grid h-screen place-items-center">
        <Spinner />
      </div>
    );

  return (
    <div className="h-full w-full bg-onboarding-gradient-100">
      <div className="flex items-center justify-between px-8 pb-4 sm:px-16 sm:py-5 lg:px-28">
        <div className="flex items-center gap-x-2 py-10">
          <Image src="https://edu-block-pro-images.s3.ap-south-1.amazonaws.com/blockalige.png" height={60} width={150} alt="BlockAgile Logo" className="mr-2" />
        </div>
      </div>

      <div className="mx-auto h-full rounded-t-md border-x border-t border-custom-border-200 bg-onboarding-gradient-100 px-4 pt-4 shadow-sm sm:w-4/5 md:w-2/3">
        <div className="h-full overflow-auto rounded-t-md bg-onboarding-gradient-200 px-7 pb-56 pt-24 sm:px-0">
          <SignInRoot />
        </div>
      </div>
    </div>
  );
});
