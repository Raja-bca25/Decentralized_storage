// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.20;
contract SecureStorage{
    struct File{
        string ipfsHash;
        string nonce;
        string tag;
    }
    mapping(address => File[])
private userFiles;
    event FileStored(address indexed user,string ipfsHash,string nonce,string tag);
    function storeFile(string memory ipfsHash,string memory nonce,string memory tag) public{
        userFiles[msg.sender].push(File(ipfsHash,nonce,tag));
        emit FileStored(msg.sender,ipfsHash,nonce,tag);
    }
    function getFiles()public view returns (File[] memory){
        return userFiles[msg.sender];
    }
}