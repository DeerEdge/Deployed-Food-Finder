import streamlit as st
from django_api.models import Entity, Producer, FoodItem, FoodType
from pages.Django_Login import check_password

# if user is logged in:
    # check if user has a producer account linked:
        # display if so
        # display register for a producer account if not
    # check if user has a volunteer account linked:
        # display if so
        # display register for a volunteer account if not
        ## optional: have a saved/bookmarked locations?
# else (not logged in):
    # prompt check_password

# on the scatter2 map,
    ## optional: registered volunteers can bookmark
    # if producer, highlight the locations that are registered as yours

st.title("My Profile")




def get_user_entity():
    current_user = st.session_state["user"]
    entity = Entity.objects.all().filter(user=current_user).first()
    return entity

def get_producer():
    try:
        return Producer.objects.all().filter(entity=get_user_entity()).first()
    except AttributeError:
        return None

def get_food_items():
    try:
        return FoodItem.objects.all().filter(producer=get_producer())
    except AttributeError:
        return None

def get_food_types():
    return FoodType.objects.all()

# first login is a user
if check_password():
    current_user = st.session_state["user"]
    current_entity = get_user_entity()

    left_column, right_column = st.columns(2)
    with left_column:
        first_name_input = st.text_input(label="**First name or Organization name***", value=current_user.first_name)

    with right_column:
        last_name_input = st.text_input(label="Last name", value=current_user.last_name)

    with st.container():
        email_input = st.text_input(label="Email address", value=current_user.email)

    with st.container():
        st.subheader("Additional Info")
        if (get_user_entity()):
            phone_number_input = st.text_input(label="Phone number", value=get_user_entity().phone_number)
            col1, col2 = st.columns(2)
            with col1:
                latitude_input = st.text_input(label="**Latitude***", value=get_user_entity().latitude)
            with col2:
                longitude_input = st.text_input(label="**Longitude***", value=get_user_entity().longitude)
            address_input = st.text_input(label="Address", value=get_user_entity().address)
        else:
            phone_number_input = st.text_input(label="Phone number")
            col1, col2 = st.columns(2)
            with col1:
                latitude_input = st.text_input(label="**Latitude***")
            with col2:
                longitude_input = st.text_input(label="**Longitude***")
            address_input = st.text_input(label="Address")


    def name_clean():
        if first_name_input == "":
            st.warning('First name or Organization name is required!', icon="⚠️")
            return False
        else:
            return True

    def latitude_clean():
        if latitude_input == "":
            st.warning('Latitude is required!', icon="⚠️")
            return False
        # some other verification that latitude are within bounds
        try:
            float(latitude_input)
            return True
        except ValueError:
            st.warning('Latitude must be a valid decimal!', icon="⚠️")
            return False

    def longitude_clean():
        if longitude_input == "":
            st.warning('Longitude is required!', icon="⚠️")
            return False
        # some other verification that longitude are within bounds
        try:
            float(latitude_input)
            return True
        except ValueError:
            st.warning('Longitude must be a valid decimal!', icon="⚠️")
            return False


    def post_to_db(entity):
        current_user.first_name = first_name_input
        current_user.last_name = last_name_input
        current_user.email = email_input

        current_user.save()

        if entity is None:
            if latitude_input != "" and longitude_input != "":
                new_entity = Entity.objects.create(user=current_user,
                                                   phone_number=phone_number_input,
                                                   latitude=latitude_input,
                                                   longitude=longitude_input,
                                                   address=address_input)
                new_entity.save()
        else:
            current_entity.phone_number = phone_number_input
            current_entity.latitude = latitude_input
            current_entity.longitude = longitude_input
            current_entity.address = address_input
            current_entity.save()

    if st.button("Save Profile"):
        if (name_clean()
            and latitude_clean()
            and longitude_clean()
        ):
            post_to_db(current_entity)
            st.toast("Account successfully updated!", icon="✅")

    st.subheader("Associated Account Details")

    if get_producer() is not None:
        current_producer = get_producer()
        st.write("You have an associated producer account.")
        with st.expander("See producer account details:"):
            st.write(f"**{current_producer}**")
            st.write(f"Deliveries: {current_producer.deliveries}")
            producer_description_input = st.text_area(label="Description", value=current_producer.description)
            website_input = st.text_input(label="Website", value=current_producer.website_link)
            if(st.button("Save changes")):
                current_producer.description = producer_description_input
                current_producer.website = website_input
                current_producer.save()

        with st.expander("See producer inventory:"):
            st.markdown("**Inventory:**")
            count = 0
            create_widget = True
            while count < get_food_items().count():
                if create_widget:
                    st.write("**Add a food item:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        food_name_input = st.text_input(label="Food name")
                    with col2:
                        food_type_input = st.selectbox("Food type", get_food_types(), key="create")
                    food_item_description_input = st.text_area(label="Food description")

                    count = -1
                    create_widget=False

                else:
                    food_item = get_food_items()[count]
                    col1, col2 = st.columns(2)
                    with col1:
                        food_name_input = st.text_input(label="Food name",value=f"{food_item.name}",key=f"food_item{count}")
                    with col2:
                        food_type_input = st.selectbox("Food type", get_food_types(), key=get_food_types()[count])
                    food_item_description_input = st.text_area(label="Food description",value=food_item.description)

                def food_name_clean():
                    if food_name_input == "":
                        st.warning('Food name is required!', icon="⚠️")
                        return False
                    else:
                        return True

                def food_description_clean():
                    if food_item_description_input == "":
                        st.warning('Food description is required!', icon="⚠️")
                        return False
                    else:
                        return True

                if st.button("Save changes", key="button" + str(count)):
                    if (food_name_clean()
                        and food_description_clean()
                    ):
                        try:
                            food_item.name = food_name_input
                            food_item.type = food_type_input
                            food_item.description = food_item_description_input
                            food_item.save()
                        except NameError:
                            food_item = FoodItem.objects.create(
                                name=food_name_input,
                                type=food_type_input,
                                description=food_item_description_input,
                                producer=current_producer,
                            )
                            food_item.save()
                        st.toast("Food Item successfully saved!",icon="✅")


                st.divider()
                count += 1
    else:
        st.write("You do not have an associated producer account. Register now?")

else:
    st.markdown("You are not currently logged in. Log in?")


