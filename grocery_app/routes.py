from flask import Blueprint, request, render_template, redirect, url_for, flash
from datetime import date, datetime
from grocery_app.models import GroceryItem, GroceryStore, User
from flask_login import login_user, logout_user, login_required, current_user
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, SignUpForm, LoginForm, AddToCartForm

# Import app and db from events_app package so that we can run app
from grocery_app.extensions import app, db, bcrypt

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    logged_in = current_user.is_authenticated
    print(logged_in)
    return render_template('home.html', all_stores=all_stores, logged_in=logged_in)

@main.route('/new_store', methods=['GET', 'POST'])
def new_store():
    # TODO: Create a GroceryStoreForm
    form = GroceryStoreForm()
    # TODO: If form was submitted and was valid:
    # - create a new GroceryStore object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the store detail page.
    if form.validate_on_submit():
        new_store = GroceryStore(
            title=form.title.data,
            address=form.address.data,
        )
        db.session.add(new_store)
        db.session.commit()

        flash("store added")
        return redirect(url_for('main.store_detail', store_id = new_store.id))

    

    # TODO: Send the form to the template and use it to render the form fields
    return render_template('new_store.html', form=form)

@main.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    # TODO: Create a GroceryItemForm
    form = GroceryItemForm()

    # TODO: If form was submitted and was valid:
    # - create a new GroceryItem object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the item detail page.
    if form.validate_on_submit():
        new_item = GroceryItem(
            name=form.name.data,
            category=form.category.data,
            price=form.price.data,
            photo_url=form.photo_url.data,
            store_id=form.store.data.id
        )
        db.session.add(new_item)
        db.session.commit()

        flash("item added")

        return redirect(url_for('main.item_detail', item_id = new_item.id))

    # TODO: Send the form to the template and use it to render the form fields
    return render_template('new_item.html', form=form)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    # TODO: Create a GroceryStoreForm and pass in `obj=store`
    form = GroceryStoreForm(obj=store)

    # TODO: If form was submitted and was valid:
    # - update the GroceryStore object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the store detail page.
    if form.validate_on_submit():
        store.title = form.title.data
        store.address = form.address.data

        db.session.add(store)
        db.session.commit()

        flash("store updated")

        return redirect(url_for('main.store_detail', store_id = store.id))

    # TODO: Send the form to the template and use it to render the form fields
    store = GroceryStore.query.get(store_id)
    return render_template('store_detail.html', store=store, form=form)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    # TODO: Create a GroceryItemForm and pass in `obj=item`
    form = GroceryItemForm(obj=item)

    # TODO: If form was submitted and was valid:
    # - update the GroceryItem object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the item detail page.
    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.category = form.category.data
        item.photo_url = form.photo_url.data
        item.store = form.store.data

        db.session.add(item)
        db.session.commit()

        flash(f"item({item.name}) updated")

        return redirect(url_for('main.item_detail', item = item))

    # TODO: Send the form to the template and use it to render the form fields
    item = GroceryItem.query.get(item_id)
    return render_template('item_detail.html', item=item, form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        print('created')
        return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))

@main.route('/add_to_shopping_list/<item_id>', methods=['GET', 'POST'])
@login_required
def add_to_shopping_list(item_id):
    shopping_list = current_user.shopping_list_items


    item = GroceryItem.query.get(item_id)
    current_user.shopping_list_items.append(item)

    db.session.commit()

    flash("item added to cart")

    return redirect(url_for('main.view_cart', user_id=current_user.id))


@main.route('/view_cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    user = current_user

    # TODO send users grocery list to html page for editing/viewing
    items = db.session.query(User).filter_by(id=user.id).first().shopping_list_items
    # user_
    # test = User.query.filter_by(id = user.id).join(GroceryItem).filter(GroceryItem.id == User.)            
    
    return render_template('view_cart.html', items=items)
