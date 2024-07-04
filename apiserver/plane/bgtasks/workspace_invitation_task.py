# Python imports
import os
import requests
import json

# Django imports
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Third party imports
from celery import shared_task
from sentry_sdk import capture_exception
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Module imports
from plane.db.models import Workspace, WorkspaceMemberInvite, User
from plane.license.utils.instance_value import get_email_configuration


@shared_task
def workspace_invitation(email, workspace_id, token, current_site, invitor):
    print("starting ",email)
    try:
        user = User.objects.get(email=invitor)

        workspace = Workspace.objects.get(pk=workspace_id)
        workspace_member_invite = WorkspaceMemberInvite.objects.get(
            token=token, email=email
        )

        # Relative link
        relative_link = f"/workspace-invitations/?invitation_id={workspace_member_invite.id}&email={email}&slug={workspace.slug}"

        # The complete url including the domain
        abs_url = str(current_site) + relative_link

        (
            EMAIL_HOST,
            EMAIL_HOST_USER,
            EMAIL_HOST_PASSWORD,
            EMAIL_PORT,
            EMAIL_USE_TLS,
            EMAIL_FROM,
        ) = get_email_configuration()
        print("EMAIL",EMAIL_HOST,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD,EMAIL_PORT,EMAIL_USE_TLS=="1",EMAIL_FROM," done")
        # Subject of the email
        subject = f"{user.first_name or user.display_name or user.email} has invited you to join them in {workspace.name} on BlockAgile"

        context = {
            "email": email,
            "first_name": user.first_name or user.display_name or user.email,
            "workspace_name": workspace.name,
            "abs_url": abs_url,
        }

        html_content = render_to_string(
            "emails/invitations/workspace_invitation.html", context
        )

        text_content = strip_tags(html_content)

        workspace_member_invite.message = text_content
        workspace_member_invite.save()

        connection = get_connection(
            host=EMAIL_HOST,
            port=int(EMAIL_PORT),
            username=EMAIL_HOST_USER,
            password=EMAIL_HOST_PASSWORD,
            use_tls=EMAIL_USE_TLS == "1",
        )
        print("check conn ",connection)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_FROM,
            to=[email],
            connection=connection,
        )
        print("msg ",msg)
        msg.attach_alternative(html_content, "text/html")
        print("between that ")
        msg.send()
        print("sent ")

        return
    except (Workspace.DoesNotExist, WorkspaceMemberInvite.DoesNotExist) as e:
        print("Workspace or WorkspaceMember Invite Does not exists")
        return
    except Exception as e:
        # Print logs if in DEBUG mode
        print("cahid uhsod",e)
        if settings.DEBUG:
            print(e)
        capture_exception(e)
        return
