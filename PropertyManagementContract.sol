// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PropertyManagement is ERC721Enumerable, Ownable {
    struct Property {
        string name;
        uint256 price;
        uint256 _size;
        uint256 quantity;
    }

    Property[] public properties;

   constructor(address initialOwner) ERC721("PropertyManagement", "PM") Ownable(initialOwner) {}

    function mint(string memory _name, uint256 _size, uint256 _price) public onlyOwner {
    properties.push(Property(_name, _size, _price));
    uint256 newPropertyId = properties.length - 1;
    _mint(msg.sender, newPropertyId);
}

    function listProperties() public view returns (Property[] memory) {
        return properties;
    }

    function buyProperty(uint256 propertyId) public payable {
        require(propertyId < properties.length, "Property does not exist");
        require(msg.value >= properties[propertyId].price, "Not enough Ether");

        _transfer(ownerOf(propertyId), msg.sender, propertyId);
    }

    function sellProperty(uint256 propertyId) public {
        require(msg.sender == ownerOf(propertyId), "Not the owner");

        _transfer(msg.sender, owner(), propertyId);
        payable(msg.sender).transfer(properties[propertyId].price);
    }
}
