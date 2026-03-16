from ninja import Router, Form, File
from django.db import transaction
from ninja.files import UploadedFile

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth
from accounts.models import User
from accounts.schemas import SuccessSchema, ErrorSchema
from property.models import State, PropertyManagement, Unit, UnitType, UnitClass, Images, UnitForm
from property.schemas import AddProperty, AssignManager, PropertySchema, AddEditUnit, UploadUnitImage, UploadUnitForm
from accounts.constants import PROPERTY_MANAGER, SUPER_ADMIN, OPERATOR
from property.services import update_property_forms
from forms.models import Forms
from property.models import PropertyForms

router = Router(tags=["property"])


#  *************************** ADMIN **************************************
@router.post(
    "/admin/assign-manager",
    auth=SuperAdminAuth(),
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def assign_manager(request, payload: AssignManager):
    user = User.objects.get(id=payload.manager_id)
    if not user:
        return 400, {
            "status": "ERROR",
            "message": "User not found",
        }
    if user.role.id is not PROPERTY_MANAGER:
        return 400, {
            "status": "ERROR",
            "message": "Assigned user is not a property manager",
        }
    try:
        with transaction.atomic():
            property_management = PropertyManagement.objects.get(id=payload.property_id)
            if not property_management:
                return 400, {
                    "status": "ERROR",
                    "message": "Property does not exist",
                }

            property_management.manager = user
            property_management.save()

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully update property manager.",
        "data": None
    }


#  *************************** PROPERT MANAGER **************************************


#  *************************** OPERATOR **************************************


#  *************************** ALL **************************************

@router.post(
    "/add-edit",
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def add_edit_property(request, payload: AddProperty):
    try:
        state = State.objects.get(id=payload.state_id)
        with transaction.atomic():
            if payload.id:
                property_management = PropertyManagement.objects.get(id=payload.id)
                property_management.name = payload.name
                property_management.property_management_company = payload.property_management_company
                property_management.address_line_1 = payload.address_line_1
                property_management.address_line_2 = payload.address_line_2
                property_management.city = payload.city
                property_management.zipcode = payload.zipcode
                property_management.state = state
                if request.user.role.id is OPERATOR:
                    property_management.state_registration = payload.state_registration
                if request.user.role.id is SUPER_ADMIN:
                    user = User.objects.get(id=payload.manager_id)
                    if not user:
                        return 400, {
                            "status": "ERROR",
                            "message": "User not found",
                        }
                    if user.role.id is not PROPERTY_MANAGER:
                        return 400, {
                            "status": "ERROR",
                            "message": "Assigned user is not a property manager",
                        }
                    property_management.state_registration = payload.state_registration
                    property_management.manager_id = payload.manager_id
                property_management.save()
                if request.user.role.id is PROPERTY_MANAGER:
                    update_property_forms(property_management, payload)

            else:
                print(request.user.role)
                if request.user.role.id is not OPERATOR:
                    return 400, {
                        "status": "ERROR",
                        "message": "Can't add building details",
                    }

                property_management = PropertyManagement.objects.create(
                    name=payload.name,
                    state_registration=payload.state_registration,
                    property_management_company=payload.property_management_company,
                    address_line_1=payload.address_line_1,
                    address_line_2=payload.address_line_2,
                    city=payload.city,
                    zipcode=payload.zipcode,
                    state=state,
                    created_by=request.user,
                )
                if not property_management:
                    return 400, {
                        "status": "ERROR",
                        "message": "Form could not be created.",
                    }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully added/updated building.",
        "data": None
    }


@router.get(
    "/get",
    response={200: SuccessSchema[list[PropertySchema]], 400: ErrorSchema},
)
def get_property(request):
    buildings = []
    if request.user.role.id is PROPERTY_MANAGER:
        buildings = (
            PropertyManagement.objects
            .select_related("state")
            .filter(manager=request.user)
        )

    if request.user.role.id is OPERATOR:
        buildings = (
            PropertyManagement.objects
            .select_related("state")
            .filter(created_by=request.user)
        )

    if request.user.role.id is SUPER_ADMIN:
        buildings = (
            PropertyManagement.objects
            .select_related("state")
        )

    result = []

    for building in buildings:

        state_forms = Forms.objects.filter(state=building.state).select_related("state")

        active_forms = set(
            PropertyForms.objects
            .filter(property=building)
            .values_list("form_id", flat=True)
        )
        print(active_forms)

        forms = []

        if request.user.role.id in [PROPERTY_MANAGER, SUPER_ADMIN]:
            for form in state_forms:
                forms.append({
                    "id": form.id,
                    "name": form.name,
                    "image": form.image.url if form.image else None,
                    "unit_type": form.unit_type.name,
                    "active": 1 if form.id in active_forms else 0
                })

        if request.user.role.id is OPERATOR:
            for form in state_forms:
                if form.id in active_forms:
                    forms.append({
                        "id": form.id,
                        "name": form.name,
                        "image": form.image.url if form.image else None,
                        "unit_type": form.unit_type.name,
                        # "active": 1 if form.id in active_forms else 0
                    })

        result.append({
            "id": building.id,
            "name": building.name,
            "address_line_1": building.address_line_1,
            "address_line_2": building.address_line_2,
            "city": building.city,
            "zipcode": building.zipcode,
            "property_management_company": building.property_management_company,
            "state_registration": building.state_registration,
            "state": {
                "id": building.state.id,
                "name": building.state.name
            },
            "forms": forms
        })

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetched buildings.",
        "data": result
    }


@router.post(
    "/unit/add-edit",
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def add_edit_unit(request, payload: AddEditUnit = Form(...), certificate: UploadedFile = File(None)):
    try:
        unit_type  = UnitType.objects.get(id=payload.unit_type)
        unit_class  = UnitClass.objects.get(id=payload.unit_class)
        property_management = PropertyManagement.objects.get(id=payload.property)
        with transaction.atomic():
            if payload.id:
                unit = Unit.objects.get(id=payload.id)
                unit.nickname = payload.nickname
                unit.state_registration = payload.state_registration
                unit.unit_type = unit_type
                unit.unit_class = unit_class
                if request.user.role.id is PROPERTY_MANAGER:
                    unit.expiration_date = payload.expiration_date
                    if unit.certificate:
                        unit.certificate.delete(save=False)

                    unit.certificate = certificate
                unit.save()

            else:
                if request.user.role.id is not OPERATOR:
                    return 400, {
                        "status": "ERROR",
                        "message": "Can't add building details",
                    }
                unit = Unit.objects.create(
                    nickname = payload.nickname,
                    state_registration = payload.state_registration,
                    unit_type = unit_type,
                    unit_class = unit_class,
                    user = request.user,
                    property=property_management,
                )
                if not unit:
                    return 400, {
                        "status": "ERROR",
                        "message": "Unit could not be created.",
                    }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully added/updated unit.",
        "data": None
    }


@router.post(
    "/unit/add-image",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def add_unit_image(
    request,
    payload: UploadUnitImage = Form(...),
    image: UploadedFile = File(...)
):
    try:
        unit = Unit.objects.get(id=payload.unit_id)

        with transaction.atomic():
            img = Images.objects.create(
                user=request.user,
                unit=unit,
                property=unit.property,
                url=image
            )

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully added image.",
            "data": {
                "image_id": img.id,
                "image_url": img.url.url if img.url else None
            }
        }

    except Unit.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Unit not found"}

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.post(
    "/unit/add-form",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def add_unit_image(
    request,
    payload: UploadUnitForm = Form(...),
    image: UploadedFile = File(...)
):
    try:
        unit = Unit.objects.get(id=payload.unit_id)

        with transaction.atomic():
            img = UnitForm.objects.create(
                user=request.user,
                unit=unit,
                form_name=payload.form_name,
                expiration_date=payload.expiration_date,
                property=unit.property,
                url=image
            )

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully added image.",
            "data": {
                "image_id": img.id,
                "image_url": img.url.url if img.url else None
            }
        }

    except Unit.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Unit not found"}

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}