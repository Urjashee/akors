from typing import Optional
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3
from botocore.exceptions import NoCredentialsError

from ninja import Router
from django.db import transaction
from ninja import File
from django.core.files.uploadedfile import UploadedFile

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.schemas import SuccessSchema, ErrorSchema
from forms.models import Forms
from property.models import State
from forms.schemas import AddProperty, UpdateStates, AddEditForms, DeleteForm

router = Router(tags=["forms"])

#  *************************** ADMIN **************************************
@router.post(
    "/update-states",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def update_states(request, payload: UpdateStates):
    try:
        with transaction.atomic():
            for state_id in payload.states:
                state = State.objects.get(pk=state_id)
                state.is_active = True
                state.save()

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully updated states.",
    }


@router.post(
    "/add-edit",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def add_update_form(request, payload: AddEditForms, image: Optional[UploadedFile] = File(None)):
    try:
        with transaction.atomic():
            if payload.id:
                form = Forms.objects.get(id=payload.id)
                form.name = payload.name
                form.state_id = payload.state_id

                if image:
                    if form.image:
                        form.image.delete(save=False)

                    form.image = image
                    form.save()

            else:
                form = Forms.objects.create(
                    name=payload.name,
                    state_id=payload.state_id,
                    image=image if image else None
                )

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully added/updated form.",
    }


@router.post(
    "/delete",
    auth=SuperAdminAuth(),
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def delete_form(request, payload: DeleteForm):

    try:
        with transaction.atomic():

            form = Forms.objects.get(id=payload.id)

            if form.image:
                form.image.delete(save=False)

            form.delete()

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully deleted form.",
    }


#  *************************** PROPERT MANAGER **************************************



#  *************************** OPERATOR **************************************
