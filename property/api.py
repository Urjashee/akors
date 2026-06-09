from typing import List
from ninja import Router, Form, File, Query
from django.db import transaction
from ninja.files import UploadedFile
from django.db.models import Q

from accounts.auth_roles_middleware import OperatorAuth, SuperAdminAuth, SuperAdminOrPropertyManagerAuth, \
    PropertyManagerAuth
from accounts.auth import get_user_from_token
from accounts.models import User
from accounts.schemas import SuccessSchema, ErrorSchema
from accounts.services import operator_details, property_manager_details
from property.models import State, PropertyManagement, Unit, UnitType, UnitClass, Images, UnitForm
from property.schemas import AddProperty, AssignManager, PropertySchema, AddEditUnit, UploadUnitImage, UploadUnitForm, \
    UnitSchema, PropertyListData, UnitListData, AddUnitByAddress, AddUnitByAddressResponse, AssignFormToImage, \
    VisibilitySchema
from core.pagination import PaginationSchema, paginate_queryset
from accounts.constants import PROPERTY_MANAGER, SUPER_ADMIN, OPERATOR
from property.services import update_property_forms, get_building_details, get_unit_details, check_if_subscription, add_unit_visibility
from forms.models import Forms
from property.models import PropertyForms
from stripe_integration.services import get_all_invoice, get_invoice_details

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


@router.get(
    "/get-user-details/{user_id}",
    auth=SuperAdminOrPropertyManagerAuth(),
    response={200: SuccessSchema, 400: ErrorSchema},
)
def get_user_details(request, user_id: int):
    buildings = []
    property_management = []
    history = []
    fetch_user_details = None
    user = User.objects.get(id=user_id)

    if not user.customer_id:
        history = []
    else:
        invoices = get_all_invoice(user.customer_id)
        for invoice in invoices.data:
            fetch_invoice_details = get_invoice_details(invoice)
            history.append(fetch_invoice_details)

    if user.role.id == OPERATOR:
        property_management = (
            PropertyManagement.objects
            .select_related("state")
            .filter(created_by=user_id)
        )
        fetch_user_details = operator_details(user)

    if user.role.id == PROPERTY_MANAGER:
        property_management = (
            PropertyManagement.objects
            .select_related("state")
            .filter(manager=user_id)
        )
        fetch_user_details = property_manager_details(user)

    for properties in property_management:
        unit_count = Unit.objects.filter(property=properties).count()
        fetch_building_details = get_building_details(properties)
        fetch_building_details["unit_count"] = unit_count
        buildings.append(fetch_building_details)

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetch user details.",
        "data": {
            "user": fetch_user_details,
            "property": buildings,
            "payment_history": history,
        }
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
                previous_state_id = property_management.state_id
                property_management.name = payload.name
                property_management.property_management_company = payload.property_management_company
                property_management.address_line_1 = payload.address_line_1
                property_management.address_line_2 = payload.address_line_2
                property_management.city = payload.city
                property_management.zipcode = payload.zipcode
                property_management.state = state

                if request.user.role.id == SUPER_ADMIN:
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
                    # property_management.state_registration = payload.state_registration
                    property_management.manager_id = payload.manager_id
                property_management.save()

                if previous_state_id != state.id:
                    PropertyForms.objects.filter(property=property_management).delete()

                if request.user.role.id == PROPERTY_MANAGER:
                    update_property_forms(property_management, payload)

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
    response={200: SuccessSchema[PropertyListData], 400: ErrorSchema},
)
def get_property(request, pagination: PaginationSchema = Query(...)):
    buildings = PropertyManagement.objects.select_related("state")

    if request.user.role.id == PROPERTY_MANAGER:
        buildings = buildings.filter(manager=request.user)
    elif request.user.role.id == OPERATOR:
        buildings = buildings.filter(created_by=request.user)

    page_data = paginate_queryset(buildings, pagination.current_page, pagination.page_size)

    result = []
    for building in page_data["items"]:

        unit_count = Unit.objects.filter(property=building).count()
        state_forms = Forms.objects.filter(state=building.state).select_related("state")

        active_forms = set(
            PropertyForms.objects
            .filter(property=building)
            .values_list("form_id", flat=True)
        )

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

        if request.user.role.id == OPERATOR:
            for form in state_forms:
                if form.id in active_forms:
                    forms.append({
                        "id": form.id,
                        "name": form.name,
                        "image": form.image.url if form.image else None,
                        "unit_type": form.unit_type.name,
                    })

        fetch_building_details = get_building_details(building)
        fetch_building_details["forms"] = forms
        fetch_building_details["unit_count"] = unit_count
        result.append(fetch_building_details)

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetched buildings.",
        "data": {
            "properties": result,
            "current_page": page_data["current_page"],
            "page_size": page_data["page_size"],
            "total": page_data["total"],
            "total_pages": page_data["total_pages"],
        },
    }


@router.get(
    "/search",
    auth=None,
    response={200: SuccessSchema[PropertyListData], 400: ErrorSchema},
)
def search_property(request, query: str = "", pagination: PaginationSchema = Query(...)):
    try:
        buildings = PropertyManagement.objects.select_related("state")

        if query:
            buildings = buildings.filter(
                Q(name__icontains=query) |
                Q(property_management_company__icontains=query) |
                Q(address_line_1__icontains=query) |
                Q(address_line_2__icontains=query) |
                Q(city__icontains=query) |
                Q(zipcode__icontains=query) |
                Q(state__name__icontains=query)
            )

        page_data = paginate_queryset(buildings, pagination.current_page, pagination.page_size)

        result = []
        for building in page_data["items"]:

            unit_count = Unit.objects.filter(property=building).count()
            state_forms = Forms.objects.filter(state=building.state)

            active_forms = set(
                PropertyForms.objects
                .filter(property=building)
                .values_list("form_id", flat=True)
            )

            forms = []
            for form in state_forms:
                if form.id in active_forms:
                    forms.append({
                        "id": form.id,
                        "name": form.name,
                        "image": form.image.url if form.image else None,
                        "unit_type": form.unit_type.name,
                    })

            data = get_building_details(building)
            data["forms"] = forms
            data["unit_count"] = unit_count
            result.append(data)

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully fetched buildings.",
            "data": {
                "properties": result,
                "current_page": page_data["current_page"],
                "page_size": page_data["page_size"],
                "total": page_data["total"],
                "total_pages": page_data["total_pages"],
            },
        }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }


@router.get(
    "/search-building",
    auth=None,
    response={200: SuccessSchema[PropertyListData], 400: ErrorSchema},
)
def search_building(request, query: str = "", pagination: PaginationSchema = Query(...)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else None
    current_user = get_user_from_token(token) if token else None
    is_authenticated = current_user is not None

    try:
        buildings = PropertyManagement.objects.select_related("state", "manager")

        if is_authenticated:
            if current_user.role.id == PROPERTY_MANAGER:
                buildings = buildings.filter(manager=current_user)
            elif current_user.role.id == OPERATOR:
                buildings = buildings.filter(created_by=current_user)

        if not is_authenticated and (not query or not query.strip()):
            return 400, {"status": "ERROR", "message": "Query cannot be empty."}

        if query and query.strip():
            buildings = buildings.filter(
                Q(name__icontains=query) |
                Q(property_management_company__icontains=query) |
                Q(address_line_1__icontains=query) |
                Q(address_line_2__icontains=query) |
                Q(city__icontains=query) |
                Q(zipcode__icontains=query) |
                Q(state__name__icontains=query)
            )

        page_data = paginate_queryset(buildings, pagination.current_page, pagination.page_size)

        result = []
        for building in page_data["items"]:
            unit_count = Unit.objects.filter(property=building).count()
            state_forms = Forms.objects.filter(state=building.state).select_related("state")
            active_forms = set(
                PropertyForms.objects.filter(property=building).values_list("form_id", flat=True)
            )
            forms = []

            if is_authenticated and current_user.role.id in [PROPERTY_MANAGER, SUPER_ADMIN]:
                for form in state_forms:
                    forms.append({
                        "id": form.id,
                        "name": form.name,
                        "image": form.image.url if form.image else None,
                        "unit_type": form.unit_type.name,
                        "active": 1 if form.id in active_forms else 0,
                    })
            else:
                for form in state_forms:
                    if form.id in active_forms:
                        forms.append({
                            "id": form.id,
                            "name": form.name,
                            "image": form.image.url if form.image else None,
                            "unit_type": form.unit_type.name,
                        })

            fetch_building_details = get_building_details(building)
            fetch_building_details["forms"] = forms
            fetch_building_details["unit_count"] = unit_count

            if (
                is_authenticated
                and current_user.role.id == PROPERTY_MANAGER
                and building.manager_id == current_user.id
            ):
                fetch_building_details["has_visible_units"] = Unit.objects.filter(
                    property=building, visibility=True
                ).exists()
            else:
                fetch_building_details["has_visible_units"] = True

            result.append(fetch_building_details)

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully fetched buildings.",
            "data": {
                "properties": result,
                "current_page": page_data["current_page"],
                "page_size": page_data["page_size"],
                "total": page_data["total"],
                "total_pages": page_data["total_pages"],
            },
        }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }


@router.post(
    "/unit/add-edit",
    response={200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema},
)
def add_edit_unit(request, payload: AddEditUnit = Form(...), certificate: UploadedFile = File(None)):
    # check_subscription = check_if_subscription(payload, request.user)
    # if not check_subscription:
    #     return 400, {
    #         "status": "ERROR",
    #         "message": "Exceeded subscription limit!",
    #     }
    try:
        unit_type = UnitType.objects.get(id=payload.unit_type)
        unit_class = UnitClass.objects.get(id=payload.unit_class)
        property_management = PropertyManagement.objects.get(id=payload.property)
        with transaction.atomic():
            if payload.id:
                unit = Unit.objects.get(id=payload.id)
                unit.nickname = payload.nickname
                unit.state_registration = payload.state_registration
                unit.unit_type = unit_type
                unit.unit_class = unit_class
                if request.user.role.id == PROPERTY_MANAGER:
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
                    nickname=payload.nickname,
                    state_registration=payload.state_registration,
                    unit_type=unit_type,
                    unit_class=unit_class,
                    user=request.user,
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
        images: List[UploadedFile] = File(...)
):
    try:
        if len(images) > 5:
            return 400, {"status": "ERROR", "message": "Cannot upload more than 5 images at a time."}

        unit = Unit.objects.get(id=payload.unit_id)

        with transaction.atomic():
            created = [
                Images.objects.create(
                    user=request.user,
                    unit=unit,
                    property=unit.property,
                    url=image
                )
                for image in images
            ]

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully added image.",
            "data": [
                {"image_id": img.id, "image_url": img.url.url if img.url else None}
                for img in created
            ]
        }

    except Unit.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Unit not found"}

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.post(
    "/unit/add-form",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def add_unit_form(
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


@router.delete(
    "/unit/delete-form/{unit_form_id}",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def delete_unit_form(
        request, unit_form_id: int,
):
    try:
        unit_form = UnitForm.objects.get(id=unit_form_id)
        if not unit_form.id:
            return 400, {
                "status": "ERROR",
                "message": "Unit form could not be found.",
            }
        with transaction.atomic():
            unit_form.delete()

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully deleted unit form.",
        }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.delete(
    "/unit/delete-image/{unit_form_id}",
    auth=SuperAdminOrPropertyManagerAuth(),
    response={200: SuccessSchema, 400: ErrorSchema},
)
def delete_unit_image(
        request, unit_form_id: int,
):
    try:
        unit_image = Images.objects.get(id=unit_form_id)
        if not unit_image.id:
            return 400, {
                "status": "ERROR",
                "message": "Unit form could not be found.",
            }
        with transaction.atomic():
            unit_image.delete()

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully deleted unit image.",
        }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.patch(
    "/unit/image/{image_id}/{property_id}/assign-form",
    auth=SuperAdminOrPropertyManagerAuth(),
    response={200: SuccessSchema, 400: ErrorSchema},
)
def assign_form_to_image(request, image_id: int, property_id: int, payload: AssignFormToImage):
    try:
        image = Images.objects.get(id=image_id)
        property_form = PropertyForms.objects.get(form=payload.form_id, property=property_id)
        if not property_form:
            return 400, {
                "status": "ERROR",
                "message": "Property form could not be found.",
            }

        image.form = payload.form_id
        image.save()

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully assigned form to image.",
            "data": None,
        }

    except Images.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Image not found."}
    except PropertyForms.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Form not found."}
    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.get(
    "/units/get/{property_id}",
    auth=None,
    response={200: SuccessSchema[UnitListData], 400: ErrorSchema},
)
def get_units(request, property_id: int, pagination: PaginationSchema = Query(...)):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else None
    current_user = get_user_from_token(token) if token else None
    is_authenticated = current_user is not None

    units = []
    if is_authenticated:

        if current_user.role.id == SUPER_ADMIN:
            units = Unit.objects.filter(property=property_id).order_by("created_at")

        elif current_user.role.id == PROPERTY_MANAGER:
            # limit = user.subscription.units if user.subscription else 0
            units = Unit.objects.filter(property=property_id, visibility=True).order_by("created_at")

        elif current_user.role.id == OPERATOR:
            # if not user.property_id and not user.is_subscribed:
            #     return 400, {"status": "ERROR", "message": "Subscription required."}
            units = Unit.objects.filter(property=property_id).order_by("created_at")

    else:
        units = Unit.objects.filter(property=property_id).order_by("created_at")

    page_data = paginate_queryset(units, pagination.current_page, pagination.page_size)

    building = PropertyManagement.objects.select_related("state").get(id=property_id)
    state_forms = Forms.objects.filter(state=building.state).select_related("state")
    active_forms = set(
        PropertyForms.objects.filter(property=building).values_list("form_id", flat=True)
    )

    forms = []
    if is_authenticated and current_user.role.id in [PROPERTY_MANAGER, SUPER_ADMIN]:
        for form in state_forms:
            forms.append({
                "id": form.id,
                "name": form.name,
                "image": form.image.url if form.image else None,
                "unit_type": form.unit_type.name,
                "active": 1 if form.id in active_forms else 0,
            })
    else:
        for form in state_forms:
            if form.id in active_forms:
                forms.append({
                    "id": form.id,
                    "name": form.name,
                    "image": form.image.url if form.image else None,
                    "unit_type": form.unit_type.name,
                })

    data = []
    for unit in page_data["items"]:
        all_image = []
        images = Images.objects.filter(unit=unit.id)
        # print("Images", images)
        for image in images:
            all_image.append(
                {
                    "id": image.id,
                    "url": image.url.url if image.url else None,
                    "form_id": image.form.form_id if image.form_id else None,
                }
            )

        fetch_unit_data = get_unit_details(unit, forms, current_user)
        fetch_unit_data['images'] = all_image
        fetch_unit_data['forms_count'] = len(forms)
        fetch_unit_data['images_count'] = len(images)

        data.append(fetch_unit_data)

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetched units.",
        "data": {
            "units": data,
            "current_page": page_data["current_page"],
            "page_size": page_data["page_size"],
            "total": page_data["total"],
            "total_pages": page_data["total_pages"],
        },
    }


@router.post(
    "/unit/add-by-address",
    response={200: SuccessSchema[AddUnitByAddressResponse], 400: ErrorSchema},
)
def add_unit_by_address(request, payload: AddUnitByAddress):
    try:
        state = State.objects.get(id=payload.state_id)
        # unit_type = UnitType.objects.get(id=payload.unit_type)
        # unit_class = UnitClass.objects.get(id=payload.unit_class)

        with transaction.atomic():
            property_management = PropertyManagement.objects.filter(
                address_line_1__iexact=payload.address_line_1,
                address_line_2__iexact=payload.address_line_2,
                city__iexact=payload.city,
                zipcode__iexact=payload.zipcode,
                state=state,
            ).first()

            property_created = False
            if property_management is None:
                elevator_count = PropertyManagement.objects.filter(
                    name__startswith="BLDG"
                ).count()
                elevator_name = f"BLDG {str(elevator_count + 1).zfill(3)}"

                property_management = PropertyManagement.objects.create(
                    name=elevator_name,
                    property_management_company="",
                    address_line_1=payload.address_line_1,
                    address_line_2=payload.address_line_2,
                    city=payload.city,
                    zipcode=payload.zipcode,
                    state=state,
                    created_by=request.user,
                )

                state_forms = Forms.objects.filter(state=state)
                PropertyForms.objects.bulk_create([
                    PropertyForms(property=property_management, form=form)
                    for form in state_forms
                ])

                property_created = True

            if Unit.objects.filter(state_registration=payload.state_registration).exists():
                return 400, {"status": "ERROR", "message": "State registration already exists."}

            unit = Unit.objects.create(
                nickname=payload.nickname or "",
                state_registration=payload.state_registration,
                # unit_type=unit_type,
                # unit_class=unit_class,
                user=request.user,
                property=property_management,
            )
            if not unit:
                return 400, {"status": "ERROR", "message": "Unit could not be created."}

            if property_management.manager:
                add_unit_visibility(property_management.manager)

        return 200, {
            "status": "SUCCESS",
            "message": "Successfully added unit.",
            "data": {
                "unit_id": unit.id,
                "property_id": property_management.id,
                "property_name": property_management.name,
                "property_created": property_created,
            },
        }

    except State.DoesNotExist:
        return 400, {"status": "ERROR", "message": "State not found."}
    except UnitType.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Unit type not found."}
    except UnitClass.DoesNotExist:
        return 400, {"status": "ERROR", "message": "Unit class not found."}
    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.get(
    "/units/get-all",
    auth=PropertyManagerAuth(),
    response={200: SuccessSchema, 400: ErrorSchema},
)
def get_units(request, pagination: PaginationSchema = Query(...)):
    user = request.user

    buildings = PropertyManagement.objects.filter(manager=user)
    print(buildings)

    building_list = []

    for building in buildings:
        units = Unit.objects.filter(property=building)
        for unit in units:
            building_list.append({
                "id": unit.id,
                "name": unit.nickname,
                "state": unit.state_registration,
                "visibility": unit.visibility,
                "property_id": building.id,
                "property_name": building.name,
            })

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully fetched units.",
        "data": building_list
    }


@router.post(
    "/units/visibility-status",
    auth=PropertyManagerAuth(),
    response={200: SuccessSchema, 400: ErrorSchema},
)
def update_visibility(request, payload: VisibilitySchema):
    user = request.user
    limit = user.subscription.units if user.subscription else 0

    visible_count = sum(1 for item in payload.units if item.visibility)
    if visible_count > limit:
        return 400, {
            "status": "ERROR",
            "message": f"Visible units ({visible_count}) exceed subscription limit ({limit}).",
            "data": payload.units,
        }

    payload_map = {item.unit_id: item.visibility for item in payload.units}
    manager_units = Unit.objects.filter(
        property__manager=user, id__in=payload_map.keys()
    )

    if manager_units.count() != len(payload_map):
        return 400, {
            "status": "ERROR",
            "message": "One or more units do not belong to this manager.",
        }

    with transaction.atomic():
        for unit in manager_units:
            new_visibility = payload_map[unit.id]
            if unit.visibility != new_visibility:
                unit.visibility = new_visibility
                unit.save(update_fields=["visibility"])

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully updated visibility.",
        "data": {}
    }