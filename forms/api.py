from typing import Optional

from django.core.files.storage import default_storage
from ninja import Router, Form
from django.db import transaction
from ninja import File
from ninja.files import UploadedFile

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.schemas import SuccessSchema, ErrorSchema
from core import settings
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
def add_update_form(request, payload: AddEditForms = Form(...), image: UploadedFile = File(None)):
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
                    image=image
                )
                if not form:
                    return 400, {
                        "status": "ERROR",
                        "message": "Form could not be created.",
                    }
                # print("DEFAULT_FILE_STORAGE:", settings.DEFAULT_FILE_STORAGE)
                # print("STORAGE INSTANCE:", default_storage)
                # print("IMAGE:", image)
                # print("STORAGE:", form.image.storage)

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


@router.get(
    "/get/{state_id}",
    auth=SuperAdminAuth(),
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def get_forms(request, state_id: int):
    try:
        forms = Forms.objects.filter(state_id=state_id)

        data = []
        for form in forms:
            data.append({
                "id": form.id,
                "name": form.name,
                "state_id": form.state_id,
                "image": request.build_absolute_uri(form.image.url) if form.image else None
            })

        return 200, {
            "status": "SUCCESS",
            "message": "Forms fetched successfully.",
            "data": data,
        }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }


#  *************************** PROPERT MANAGER **************************************



#  *************************** OPERATOR **************************************
