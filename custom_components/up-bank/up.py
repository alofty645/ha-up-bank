import aiohttp
import logging
_LOGGER = logging.getLogger(__name__)

base = "https://api.up.com.au/api/v1"

class UP:
    api_key = ""
    def __init__(self, key):
        self.api_key = key

    async def call(self, endpoint, params={}, method="get"):
        headers = { "Authorization": "Bearer " + self.api_key }
        match method:
            case "get":
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(base + endpoint, params=params) as resp:
                        resp.data = await resp.json()
                        return resp

    async def test(self, api_key) -> bool:
        self.api_key = api_key
        result = await self.call("/util/ping")
        return result.status == 200

    async def getAccounts(self):
        result = await self.call('/accounts', {"page[size]": 100})
        if result.status != 200:
            return False

        accounts = {}
        for account in result.data['data']:
            details = BankAccount(account)
            accounts[details.id] = details
        return accounts

    async def getTransactions(self):
        result = await self.call('/transactions', {"page[size]": 100})
        if result.status != 200:
            return False

        transactions = {}
        for transaction in result.data['data']:
            account_id = transaction['relationships']['account']['data']['id']
            if account_id not in transactions:
                transactions[account_id] = []
            attrs = transaction['attributes']
            performing_customer = (attrs.get("performingCustomer", {}) or {}).get("displayName", "Unknown")
            transactions[account_id].append({
                'amount': attrs['amount']['value'],
                'description': attrs['description'],
                'who': performing_customer,
                'datetime': attrs['createdAt'],
                'status': attrs['status']
            })
        return transactions

class BankAccount:
    def __init__(self, data):
        self.name = data['attributes']['displayName']
        self.balance = data['attributes']['balance']['value']
        self.id = data['id']
        self.createdAt = data['attributes']['createdAt']
        self.accountType = data['attributes']['accountType']
        self.ownership = data['attributes']['ownershipType']
