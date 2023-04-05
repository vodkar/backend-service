from datetime import datetime
from unittest import mock


async def assert_balance(client, user, expected_balance, date=None):
    url = f'/v1/user/{user["id"]}/balance'
    if date:
        url += f'?date={date}'
    balance_resp = await client.get(url)
    assert balance_resp.status == 200
    json_resp = await balance_resp.json()
    assert json_resp['balance'] == expected_balance


async def get_transaction_id(http_client, user_id: str):
    txn_resp = await http_client.post("v1/transaction", json={"user_id": user_id})
    return (await txn_resp.json())['transaction']['id']


async def test_api(http_client):
    user_resp = await http_client.post('/v1/user', json={
        'name': 'petya'
    })

    assert user_resp.status == 201
    user = (await user_resp.json())['user']
    user_id: str = user['id']
    assert user_id > 0
    assert user['name'] == 'petya'

    await assert_balance(http_client, user, '0.00')

    txn_id = await get_transaction_id(http_client, user_id)

    txn = {
        'transaction_id': txn_id,
        'type': 'DEPOSIT',
        'amount': '100.0',
        'user_id': user_id
    }
    with mock.patch('app.models.transaction_log.datetime') as mock_datetime:
        mock_datetime.utcnow = mock.Mock(return_value=datetime(2023, 1, 4))
        txn_resp = await http_client.put('/v1/transaction', json=txn)
    assert txn_resp.status == 200
    await assert_balance(http_client, user, '100.00')

    detail_resp = await http_client.get(
        f'/v1/transaction/{txn["transaction_id"]}')
    detailed_json = (await detail_resp.json())['transaction']
    assert detailed_json['type'] == 'DEPOSIT'
    assert detailed_json['amount'] == '100.00'

    txn_id = await get_transaction_id(http_client, user_id)

    txn = {
        'transaction_id': txn_id,
        'type': 'WITHDRAW',
        'amount': '50.0',
        'user_id': user_id,
    }
    with mock.patch('app.models.transaction_log.datetime') as mock_datetime:
        mock_datetime.utcnow = mock.Mock(return_value=datetime(2023, 1, 5))
        txn_resp = await http_client.put('/v1/transaction', json=txn)
        txn_resp = await http_client.put('/v1/transaction', json=txn)
    assert txn_resp.status == 200
    await assert_balance(http_client, user, '50.00')

    txn_resp = await http_client.post("/v1/transaction", json={"user_id": user_id})
    txn_id = await get_transaction_id(http_client, user_id)

    txn = {
        'transaction_id': txn_id,
        'type': 'WITHDRAW',
        'amount': '60.0',
        'user_id': user_id,
    }
    txn_resp = await http_client.put('/v1/transaction', json=txn)
    assert txn_resp.status == 402  # insufficient funds
    await assert_balance(http_client, user, '50.00')

    txn_resp = await http_client.post("/v1/transaction", json={"user_id": user_id})
    txn_id = await get_transaction_id(http_client, user_id)

    txn = {
        'transaction_id': txn_id,
        'type': 'WITHDRAW',
        'amount': '10.0',
        'user_id': user_id
    }
    with mock.patch('app.models.transaction_log.datetime') as mock_datetime:
        mock_datetime.utcnow = mock.Mock(return_value=datetime(2023, 2, 5))
        txn_resp = await http_client.put('/v1/transaction', json=txn)
    assert txn_resp.status == 200
    await assert_balance(http_client, user, '40.00')

    await assert_balance(http_client, user, '50.00', date='2023-01-30T00:00:00.000000')
