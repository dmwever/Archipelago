all_fruits = []
all_vegetables = []


def veggie(name: str) -> str:
    all_vegetables.append(name)
    return name


def fruity(name: str) -> str:
    all_fruits.append(name)
    return name


class Fruit:
    any = "Any Fruit"
    blueberry = fruity("Blueberry")
    melon = fruity("Melon")
    apple = fruity("Apple")
    apricot = fruity("Apricot")
    cherry = fruity("Cherry")
    orange = fruity("Orange")
    peach = fruity("Peach")
    pomegranate = fruity("Pomegranate")
    banana = fruity("Banana")
    mango = fruity("Mango")
    pineapple = fruity("Pineapple")
    ancient_fruit = fruity("Ancient Fruit")
    strawberry = fruity("Strawberry")
    starfruit = fruity("Starfruit")
    rhubarb = fruity("Rhubarb")


class Vegetable:
    any = "Any Vegetable"
    parsnip = veggie("Parsnip")
    garlic = veggie("Garlic")
    wheat = veggie("Wheat")
    potato = veggie("Potato")
    corn = veggie("Corn")
    tomato = veggie("Tomato")
    pumpkin = veggie("Pumpkin")
    unmilled_rice = veggie("Unmilled Rice")
    beet = veggie("Beet")
    hops = veggie("Hops")
    cauliflower = veggie("Cauliflower")
    amaranth = veggie("Amaranth")
    kale = veggie("Kale")
    artichoke = veggie("Artichoke")
