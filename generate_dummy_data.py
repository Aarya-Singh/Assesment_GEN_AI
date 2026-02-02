import random

products = [
    "AlphaSmart Watch", "BetaBuds Wireless", "GammaCharge Pro", "DeltaTab 10", "EpsilonCam 4K",
    "ZetaSound Bar", "EtaLight Smart Bulb", "ThetaKey Mechanical Keyboard", "IotaMouse Gaming", "KappaPad Pro",
    "LambdaLink Router", "MuMic Streamer", "NuNode SSD", "XiXenon Monitor", "OmicronOscilloscope",
    "PiPrint 3D", "RhoRing Smart", "SigmaScale Body", "TauTherm Smart", "UpsilonUltra Phone"
]

features = [
    "Water resistant", "Bluetooth 5.3", "Fast charging", "OLED display", "Noise cancelling",
    "Long battery life", "Voice control", "Touch interface", "Wireless sync", "Compact design"
]

def generate_products(count=200):
    output = []
    # Keep original data
    with open("prodcut_info.txt", "r") as f:
        existing = f.read().strip()
        output.append(existing)
        output.append("\n\n# --- DUMMY CATALOG START ---\n")

    for i in range(count):
        cat_name = random.choice(products)
        p_id = f"{cat_name} v{random.randint(1, 9)}.{random.randint(0, 9)}"
        price = f"₹{random.randint(999, 49999):,}"
        feat = ", ".join(random.sample(features, k=3))
        warranty = f"{random.randint(1, 3)} year(s)"
        
        entry = f"Product: {p_id}\nPrice: {price} | Features: {feat}\nWarranty: {warranty}\n"
        output.append(entry)
    
    with open("prodcut_info.txt", "w") as f:
        f.write("\n".join(output))
    
    print(f"Successfully added {count} dummy products to prodcut_info.txt")

if __name__ == "__main__":
    generate_products(200)
