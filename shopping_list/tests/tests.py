import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shopping_list.models import ShoppingItem, ShoppingList


# Create your tests here.

@pytest.mark.django_db
def test_valid_shopping_list_created():
    url = reverse("all-shopping-lists")
    data = {
        "name": "Dairy"
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Dairy"


def test_shopping_list_name_missing_returns_bad_request():
    url = reverse("all-shopping-lists")
    data = {
        "somethingelse": "foobar"
    }
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_all_shopping_list_are_listed():
    url = reverse("all-shopping-lists")
    ShoppingList.objects.create(name="Dairy")
    ShoppingList.objects.create(name="Toys")

    client = APIClient()
    response = client.get(url)

    assert len(response.data) == 2
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["name"] == "Dairy"
    assert response.data[1]["name"] == "Toys"


@pytest.mark.django_db
def test_shopping_list_retrieved_by_id():
    shopping_list = ShoppingList.objects.create(name="Food")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_includes_only_corresponding_items():
    shopping_list_1 = ShoppingList.objects.create(name="Drinks")
    shopping_list_2 = ShoppingList.objects.create(name="Games")

    ShoppingItem.objects.create(shopping_list=shopping_list_1, name="Soda", purchased=False)
    ShoppingItem.objects.create(shopping_list=shopping_list_1, name="Coconut Water", purchased=False)
    ShoppingItem.objects.create(shopping_list=shopping_list_2, name="GTA", purchased=False)

    url = reverse("shopping-list-detail", args=[shopping_list_1.id])
    client = APIClient()
    response = client.get(url, format="json")

    assert len(response.data["shopping_items"]) == 2
    assert response.data["shopping_items"][0]["name"] == "Soda"


@pytest.mark.django_db
def shopping_list_name_is_changed():
    shopping_list = ShoppingList.objects.create(name="Toys")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    data = {
        "name": "Drinks"
    }
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingList.objects.get().name == "Drinks"
    assert response.data["name"] == "Drinks"


@pytest.mark.django_db
def test_shopping_list_not_changed_because_name_missing():
    shopping_list = ShoppingList.objects.create(name="Cloth")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    data = {
        "not_a_name": "something"
    }
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_list_name_changed_with_partial_update():
    shopping_list = ShoppingList.objects.create(name="Electrical apliances")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    data = {
        "name": "Glass"
    }
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Glass"


@pytest.mark.django_db
def test_partial_update_has_no_effect():
    shopping_list = ShoppingList.objects.create(name="Groceries")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    data = {
        "somethingelse": "notaname"
    }
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_shopping_list_is_deleted():
    shopping_list = ShoppingList.objects.create(name="Dairy")

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_valid_shopping_items_is_created():
    shopping_list = ShoppingList.objects.create(name="Meat")

    url = reverse("add-shopping-item", args=[shopping_list.id])
    client = APIClient()
    data = {
        "name": "steak",
        "purchased": False
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_missing_shopping_items_request_bad_request():
    shopping_list = ShoppingList.objects.create(name="Dairy")

    url = reverse("add-shopping-item", args=[shopping_list.id])
    client = APIClient()
    data = {
        "name": "Cheesedale"
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(create_shopping_item):
    shopping_item = create_shopping_item("Chocolate")
    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_shopping_item_purchased_status(create_shopping_item):
    shopping_item = create_shopping_item("Milk")
    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    data = {
        "name": "Milk",
        "purchased": True
    }
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["purchased"] is True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(create_shopping_item):
    shopping_item = create_shopping_item("Milk")

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    data = {
        "purchased": True
    }
    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_partial_update_shopping_item_will_return_200_ok(create_shopping_item):
    shopping_item = create_shopping_item("Milk")

    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    data = {
        "purchased": True
    }
    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["purchased"] is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(create_shopping_item):
    shopping_item = create_shopping_item("Milk")
    url = reverse("shopping-item-detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.all()) == 0
