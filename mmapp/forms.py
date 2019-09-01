from .db import get_user_by_name, update_user_info


async def validate_user_form(request, form):
    username = form.get('name')
    update_data = dict()
    if username != '':
        row = await get_user_by_name(request, username)
        print('row', row)
        if row is None:
            update_data['name'] = username

    if form.get('password') is not None:
        update_data['pwd'] = form.get('password')
    update_data['email'] = form.get('email')
    update_data['age'] = form.get('age')
    update_data['location'] = form.get('location')

    print(update_data)

    if len(update_data):
        row = await update_user_info(request, update_data, request.cookies['api_key'])
        return row
    return 0




    # if not username:
    #     return 'username is required'
    # if not password:
    #     return 'password is required'
    #
    # user = await db.get_user_by_name(conn, username)
    #
    # if not user:
    #     return 'Invalid username'
    # if not check_password_hash(password, user['password_hash']):
    #     return 'Invalid password'
    # else:
    #     return None
    #
    # return 'error'