import random

from eth_account import Account
from modules import Blockchain, Logger, Client
from modules.interfaces import SoftwareException, SoftwareExceptionWithoutRetry
from utils.tools import gas_checker, helper
from general_settings import TRANSFER_AMOUNT, WRAP_AMOUNT
from settings import (
    NATIVE_WITHDRAW_AMOUNT,
    NATIVE_DEPOSIT_AMOUNT, NATIVE_CHAIN_ID_TO,
)
from config import (
    WETH_ABI,
    TOKENS_PER_CHAIN,
    NATIVE_CONTRACTS_PER_CHAIN,
    NATIVE_ABI, CHAIN_NAME,
)


class SimpleEVM(Logger):
    def __init__(self, client):
        self.client = client
        Logger.__init__(self)

        self.network = self.client.network.name
        self.token_contract = self.client.get_contract(TOKENS_PER_CHAIN[self.network]['WETH'], WETH_ABI)
        self.deposit_contract = None
        self.withdraw_contract = None

    @helper
    @gas_checker
    async def transfer_eth_to_myself(self):

        amount = await self.client.get_smart_amount(TRANSFER_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f"Transfer {amount} ETH to your own address: {self.client.address}")

        tx_params = await self.client.prepare_transaction(value=amount_in_wei) | {
            "to": self.client.address,
            "data": "0x"
        }

        return await self.client.send_transaction(tx_params)

    @helper
    @gas_checker
    async def transfer_eth(self):

        amount = await self.client.get_smart_amount(TRANSFER_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        if amount > 0.0001:
            raise SoftwareExceptionWithoutRetry(
                'Are you sure about transferring more than 0.0001ETH to a random address?')

        random_address = Account.create().address

        self.logger_msg(*self.client.acc_info, msg=f'Transfer ETH to random address: {amount} ETH')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = (await self.client.prepare_transaction()) | {
                'to': random_address,
                'value': amount_in_wei,
                'data': "0x"
            }

            return await self.client.send_transaction(tx_params)

        else:
            raise SoftwareException('Insufficient balance!')

    @helper
    @gas_checker
    async def wrap_eth(self, amount_in_wei: int = None):

        if not amount_in_wei:
            amount = await self.client.get_smart_amount(WRAP_AMOUNT)
            amount_in_wei = self.client.to_wei(amount)
        else:
            amount = round(amount_in_wei / 10 ** 18, 5)

        self.logger_msg(*self.client.acc_info, msg=f'Wrap {amount} ETH')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = await self.client.prepare_transaction(value=amount_in_wei)
            transaction = await self.token_contract.functions.deposit().build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')

    @helper
    @gas_checker
    async def unwrap_eth(self, amount_in_wei: int = None):

        if not amount_in_wei:
            amount_in_wei, amount, _ = await self.client.get_token_balance('WETH', check_symbol=False)
        else:
            amount = round(amount_in_wei / 10 ** 18, 5)

        self.logger_msg(*self.client.acc_info, msg=f'Unwrap {amount:.6f} WETH')

        tx_params = await self.client.prepare_transaction()

        transaction = await self.token_contract.functions.withdraw(
            amount_in_wei
        ).build_transaction(tx_params)

        return await self.client.send_transaction(transaction)

    @helper
    @gas_checker
    async def random_approve(self):
        from config import (
            ODOS_CONTRACTS, ONEINCH_CONTRACTS, OPENOCEAN_CONTRACTS, RANGO_CONTRACTS,
            UNISWAP_CONTRACTS, XYFINANCE_CONTRACTS, TOKENS_PER_CHAIN
        )

        all_contracts = {
            "ODOS":ODOS_CONTRACTS,
            "1inch":ONEINCH_CONTRACTS,
            "OpenOcean":OPENOCEAN_CONTRACTS,
            "Uniswap":UNISWAP_CONTRACTS,
            "Rango":RANGO_CONTRACTS,
            "XYfinance":XYFINANCE_CONTRACTS,
        }

        amount = random.uniform(1, 1000)
        while True:
            all_network_contracts = {
                name: contracts[self.network]['router']
                for name, contracts in all_contracts.items()
                if contracts.get(self.network)
            }

            approve_contracts = [(k, v) for k, v in all_network_contracts.items()]
            contract_name, approve_contract = random.choice(approve_contracts)
            native = [self.client.token, f'W{self.client.token}']
            token_contract = random.choice(
                [i for i in list(TOKENS_PER_CHAIN[self.network].items()) if i[0] not in native]
            )
            amount *= 1.1
            amount_in_wei = self.client.to_wei(amount, await self.client.get_decimals(token_contract[0]))

            message = f"Approve {amount:.4f} {token_contract[0]} for {contract_name}"
            self.logger_msg(*self.client.acc_info, msg=message)
            result = await self.client.check_for_approved(
                token_contract[1], approve_contract, amount_in_wei, without_bal_check=True
            )

            if not result:
                raise SoftwareException('Bad approve, trying again with higher amount...')
            return result


class Scroll(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)
        self.deposit_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Scroll']['deposit'],
            NATIVE_ABI['Scroll']['deposit']
        )
        self.withdraw_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Scroll']['withdraw'],
            NATIVE_ABI['Scroll']['withdraw']
        )

        self.oracle_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Scroll']["oracle"],
            NATIVE_ABI['Scroll']['oracle']
        )

    @helper
    @gas_checker
    async def deposit(self):

        amount = await self.client.get_smart_amount(NATIVE_DEPOSIT_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Bridge {amount} ETH ERC20 -> Scroll')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            gas_limit = 168000
            gas_price = await self.client.w3.eth.gas_price

            bridge_fee = int(gas_limit * gas_price / 4)

            tx_params = await self.client.prepare_transaction(value=amount_in_wei + bridge_fee)

            transaction = await self.deposit_contract.functions.sendMessage(
                self.client.address,
                amount_in_wei,
                '0x',
                168000,
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')

    @helper
    @gas_checker
    async def withdraw(self):

        amount = await self.client.get_smart_amount(NATIVE_WITHDRAW_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Withdraw {amount} ETH Scroll -> ERC20')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = await self.client.prepare_transaction(value=amount_in_wei)

            transaction = await self.withdraw_contract.functions.withdrawETH(
                amount_in_wei,
                0
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')


class ZkSync(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)

        self.deposit_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['zkSync']['deposit'],
            NATIVE_ABI['zkSync']['deposit']
        )
        self.withdraw_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['zkSync']['withdraw'],
            NATIVE_ABI['zkSync']['withdraw']
        )

    @helper
    @gas_checker
    async def deposit(self):

        amount = await self.client.get_smart_amount(NATIVE_DEPOSIT_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Bridge on txSync: {amount} ETH ERC20 -> zkSync Era')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            gas_limit = random.randint(750000, 1000000)

            base_cost_in_wei = int((await self.deposit_contract.functions.l2TransactionBaseCost(
                await self.client.w3.eth.gas_price,
                gas_limit,
                800
            ).call()) * 1.2)

            tx_params = await self.client.prepare_transaction(value=amount_in_wei + base_cost_in_wei)

            transaction = await self.deposit_contract.functions.requestL2Transaction(
                self.client.address,
                amount_in_wei,
                "0x",
                gas_limit,
                800,
                [],
                self.client.address
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Bridge on txSync | Insufficient balance!')

    @helper
    @gas_checker
    async def withdraw(self):

        amount = await self.client.get_smart_amount(NATIVE_WITHDRAW_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Withdraw on txSync: {amount} ETH zkSync Era -> ERC20')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = await self.client.prepare_transaction(value=amount_in_wei)

            transaction = await self.withdraw_contract.functions.withdraw(
                self.client.address,
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Withdraw on txSync | Insufficient balance!')


class Base(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)

        self.deposit_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Base']['deposit'],
            NATIVE_ABI['Base']['deposit']
        )
        self.withdraw_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Base']['withdraw'],
            NATIVE_ABI['Base']['withdraw']
        )

    @helper
    @gas_checker
    async def deposit(self):

        amount = await self.client.get_smart_amount(NATIVE_DEPOSIT_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Bridge on Base Bridge: {amount} ETH ERC20 -> Base')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = await self.client.prepare_transaction(value=amount_in_wei)

            transaction = await self.deposit_contract.functions.depositTransaction(
                self.client.address,
                amount_in_wei,
                100000,
                False,
                "0x01"
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')

    @helper
    @gas_checker
    async def withdraw(self):

        amount = await self.client.get_smart_amount(NATIVE_WITHDRAW_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Withdraw on Base Bridge: {amount} ETH Base -> ERC20')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            tx_params = await self.client.prepare_transaction(value=amount_in_wei)

            transaction = await self.withdraw_contract.functions.initiateWithdrawal(
                self.client.address,
                100000,
                '0x01'
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')


class Linea(Blockchain, SimpleEVM):
    def __init__(self, client: Client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)

        self.deposit_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Linea']['deposit'],
            NATIVE_ABI['Linea']['deposit']
        )
        self.withdraw_contract = self.client.get_contract(
            NATIVE_CONTRACTS_PER_CHAIN['Linea']['withdraw'],
            NATIVE_ABI['Linea']['withdraw']
        )

    async def get_bridge_fee(self, from_l1:bool = True):
        margin = 2
        gas_limit = 106000
        new_client = await self.client.new_client(4 if from_l1 else 13)
        bridge_fee = int(margin * gas_limit * await new_client.w3.eth.gas_price)

        await new_client.session.close()
        return bridge_fee

    @helper
    @gas_checker
    async def deposit(self):

        amount = await self.client.get_smart_amount(NATIVE_DEPOSIT_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Bridge {amount} ETH ERC20 -> Linea')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            bridge_fee = await self.get_bridge_fee()

            tx_params = await self.client.prepare_transaction(value=amount_in_wei + bridge_fee)

            transaction = await self.deposit_contract.functions.sendMessage(
                self.client.address,
                bridge_fee,
                "0x"
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')

    @helper
    @gas_checker
    async def withdraw(self):

        amount = await self.client.get_smart_amount(NATIVE_WITHDRAW_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        self.logger_msg(*self.client.acc_info, msg=f'Withdraw {amount} ETH Linea -> ERC20')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            bridge_fee = await self.get_bridge_fee(from_l1=False)

            tx_params = await self.client.prepare_transaction(value=amount_in_wei + bridge_fee)

            transaction = await self.withdraw_contract.functions.sendMessage(
                amount_in_wei,
                bridge_fee,
                0
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')


class ArbitrumNova(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)


class Ethereum(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)


class Blast(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)


class Zora(Blockchain, SimpleEVM):
    def __init__(self, client):
        SimpleEVM.__init__(self, client)
        Blockchain.__init__(self, client)

    async def get_bridge_info(self, amount_in_wei, chain_to_name):
        url = f'https://api-{chain_to_name.lower()}.reservoir.tools/execute/call/v1'

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "content-type": "application/json",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122""',
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://bridge.zora.energy",
            "Referer": "https://bridge.zora.energy/",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "x-rkc-version": "1.11.2"
        }

        payload = {
            "user": self.client.address,
            "txs": [
                {
                    "to": self.client.address,
                    "value": f"{amount_in_wei}",
                    "data": "0x"
                }
            ],
            "originChainId": self.client.network.chain_id
        }

        data = (await self.make_request(
            method='POST', url=url, headers=headers, json=payload))["steps"][0]["items"][0]["data"]

        contract_address = self.client.w3.to_checksum_address(data["to"])
        tx_data = data["data"]
        value = int(data["value"])

        return contract_address, tx_data, value

    @helper
    @gas_checker
    async def bridge(self):

        amount = await self.client.get_smart_amount(NATIVE_DEPOSIT_AMOUNT)
        amount_in_wei = self.client.to_wei(amount)

        chain_to_name = CHAIN_NAME[random.choice(NATIVE_CHAIN_ID_TO)]
        contract_address, tx_data, value = await self.get_bridge_info(amount_in_wei, chain_to_name)

        self.logger_msg(
            *self.client.acc_info,
            msg=f'Bridge {amount} from {self.client.network.name} -> {chain_to_name}')

        if await self.client.w3.eth.get_balance(self.client.address) > amount_in_wei:

            transaction = await self.client.prepare_transaction(value=value) | {
                'to': contract_address,
                'data': tx_data
            }

            return await self.client.send_transaction(transaction)

        else:
            raise SoftwareException('Insufficient balance!')
