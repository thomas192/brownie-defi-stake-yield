import { useEthers } from "@usedapp/core"
import helperConfig from "../helper-config.json"
import networkMapping from "../chain-info/deployments/map.json"
import { constants } from "ethers"
import brownieConfig from "../brownie-config.json"
import dapp_img from "../dapp.png"
import eth_img from "../eth.png"
import fau_img from "../dai.png"
import { YourWallet } from "./yourWallet"

export type Token = {
    image: string
    address: string
    name: string
}

export const Main = () => {
    // Show the token value from the wallet
    // Get the address of different tokens
    // Get the balance of the users wallet

    const { chainId } = useEthers()
    const networkName = chainId ? helperConfig[String(chainId)] : "dev"

    const dappTokenAddress = chainId ? networkMapping[String(chainId)]["DappToken"][0] : constants.AddressZero
    const wethTokenAddress = chainId ? brownieConfig["networks"][networkName]["weth_token"] : constants.AddressZero
    const fauTokenAddress = chainId ? brownieConfig["networks"][networkName]["fau_token"] : constants.AddressZero

    const supportedTokens: Array<Token> = [
        {
            image: dapp_img,
            address: dappTokenAddress,
            name: "DAPP"
        },
        {
            image: eth_img,
            address: wethTokenAddress,
            name: "WETH"
        },
        {
            image: fau_img,
            address: fauTokenAddress,
            name: "DAI"
        }
    ]

    return (<YourWallet supportedTokens={supportedTokens} />)

}