"""
Script Seeding Vector Store untuk AutoBargain AI
Memasukkan 110+ dataset mobil bekas populer Indonesia & Global ke ChromaDB menggunakan SentenceTransformers.
"""

import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BACKEND_DIR / "cars_vectorstore")

# Dataset Lengkap Representatif Pasar Mobil Bekas Indonesia (110+ Cars)
SAMPLE_CARS_DATASET = [
    # ==========================================
    # 1. TOYOTA (16 Mobil)
    # ==========================================
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Avanza 1.3 G MT 2019 Silver. Odo 52.000 km. AC double blower dingin, mesin 1.3 Dual VVT-i irit bensin, bodi kaleng orisinil.", "price": 160.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Avanza 1.5 Veloz AT 2020 Putih. Odo 40.000 km. Keyless entry, retractable mirror, kamera mundur, service record Auto2000.", "price": 195.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota All New Veloz 1.5 Q CVT TSS 2022 Putih Pearl. Odo 25.000 km. Toyota Safety Sense, wireless charger, ambient light, rem parkir elektrik.", "price": 245.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Kijang Innova Reborn 2.4 G Diesel AT 2019 Hitam. Odo 65.000 km. Mesin 2GD-FTV diesel bertenaga, bodi mulus bebas banjir.", "price": 310.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Kijang Innova Reborn 2.4 V Diesel AT 2021 Hitam. Odo 55.000 km. Captain seat, ambient light, audio steering switch, istimewa.", "price": 380.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Kijang Innova Zenix 2.0 V Hybrid CVT 2023 Putih. Odo 18.000 km. Panoramic sunroof, EV mode sangat irit 1:22 km/l, dual rear entertainment screen.", "price": 490.0},
    {"brand": "Toyota", "category": "SUV", "doc": "Toyota Fortuner 2.4 VRZ Diesel 4x2 AT 2018 Putih. Odo 75.000 km. Power backdoor, jok kulit elektrik, paddle shift, pajak on.", "price": 375.0},
    {"brand": "Toyota", "category": "SUV", "doc": "Toyota Fortuner 2.8 GR Sport 4x2 AT 2022 Hitam. Odo 30.000 km. Mesin 1GD 2800cc sangat bertenaga, full bodykit GR Sport orisinil.", "price": 540.0},
    {"brand": "Toyota", "category": "SUV", "doc": "Toyota Rush 1.5 S TRD Sportivo AT 2019 Putih. Odo 58.000 km. 6 airbags, smart key engine start, kamera mundur, suspensi kokoh.", "price": 190.0},
    {"brand": "Toyota", "category": "SUV", "doc": "Toyota Raize 1.0 Turbo GR Sport CVT TSS 2022 Two-Tone Kuning Hitam. Odo 28.000 km. Turbo intercooler lincah, adaptive cruise control, lane keep assist.", "price": 220.0},
    {"brand": "Toyota", "category": "Hatchback", "doc": "Toyota Yaris 1.5 S TRD Sportivo AT 2018 Merah Joker. Odo 68.000 km. 7 Airbags, paddle shift, smart keyless, interior bersih rapi.", "price": 195.0},
    {"brand": "Toyota", "category": "Sedan", "doc": "Toyota Corolla Altis 1.8 V AT 2017 Hitam. Odo 80.000 km. Cruise control, jok elektrik kulit, suspensi sangat nyaman, rawatan resmi.", "price": 215.0},
    {"brand": "Toyota", "category": "Sedan", "doc": "Toyota Camry 2.5 V AT 2019 Hitam. Odo 45.000 km. Head-up display, blind spot monitor, wireless charging, kemewahan sedan eksekutif.", "price": 390.0},
    {"brand": "Toyota", "category": "LCGC", "doc": "Toyota Calya 1.2 G AT 2020 Abu-abu. Odo 45.000 km. Mobil 7-seater irit, head unit touch screen, pemakaian apik tangan pertama.", "price": 125.0},
    {"brand": "Toyota", "category": "LCGC", "doc": "Toyota Agya 1.2 GR Sport AT 2022 Merah. Odo 22.000 km. GR bodykit sporty, spion retract, mesin 4 silinder responsif dan hemat.", "price": 140.0},
    {"brand": "Toyota", "category": "MPV", "doc": "Toyota Alphard 2.5 G AT 2018 Putih Pearl. Odo 50.000 km. Pilot seat ottoman, dual sunroof, audio JBL surround, power sliding door dual.", "price": 890.0},

    # ==========================================
    # 2. HONDA (14 Mobil)
    # ==========================================
    {"brand": "Honda", "category": "Hatchback", "doc": "Honda Jazz 1.5 RS GK5 AT 2018 Putih Pearl. Odo 58.000 km. Cruise control, paddle shift, lampu LED projector, velg OEM mulus.", "price": 225.0},
    {"brand": "Honda", "category": "Hatchback", "doc": "Honda Jazz 1.5 RS GK5 Facelift AT 2020 Abu-abu Metalik. Odo 38.000 km. Model terakhir Jazz Indonesia, full original record dealer Honda.", "price": 255.0},
    {"brand": "Honda", "category": "Hatchback", "doc": "Honda Brio Satya 1.2 E CVT 2021 Kuning. Odo 35.000 km. Transmisi Earth Dreams CVT halus, servis record Honda, AC dingin menggigil.", "price": 150.0},
    {"brand": "Honda", "category": "Hatchback", "doc": "Honda Brio RS 1.2 CVT 2022 Hitam Crystal. Odo 26.000 km. Velg two-tone 15 inch, suspensi sport RS, spion retract with LED.", "price": 175.0},
    {"brand": "Honda", "category": "Hatchback", "doc": "Honda City Hatchback 1.5 RS CVT 2022 Meteorite Grey. Odo 29.000 km. Ultra seats multi fungsi, remote engine start, 8 speaker, kamera mundur.", "price": 265.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda WR-V 1.5 RS with Honda Sensing CVT 2023 Merah Two Tone. Odo 15.000 km. Honda Sensing lengkap (ACC, LKAS, CMBS), walk away auto lock.", "price": 270.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda HR-V 1.5 E CVT Special Edition 2019 Hitam. Odo 50.000 km. Panoramic sunroof, jok kulit hitam, smart key, rem electric park brake.", "price": 245.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda All New HR-V 1.5 SE CVT 2022 Putih Pearl. Odo 24.000 km. Panoramic glass roof, Honda Sensing, electro-static touch LED light.", "price": 360.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda CR-V 1.5 Turbo Prestige 2018 Putih. Odo 62.000 km. 7-seater, panoramic roof, power tailgate, audio premium, mesin turbo prima.", "price": 345.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda CR-V 1.5 Turbo Black Edition 2022 Hitam Crystal. Odo 28.000 km. Edisi khusus all black alloy wheels, smoked headlamp, wood grain trim.", "price": 510.0},
    {"brand": "Honda", "category": "Sedan", "doc": "Honda Civic 1.5 Turbo Sedan FC1 2018 Abu-abu Metalik. Odo 48.000 km. Full exhaust orisinil, electric seat, sunroof, kondisi sangat prima.", "price": 340.0},
    {"brand": "Honda", "category": "Sedan", "doc": "Honda Civic 1.5 Turbo Hatchback FK4 E 2019 Merah. Odo 42.000 km. Remote engine start, dual exhaust muffler tengah, kamera mundur, bodi mulus.", "price": 320.0},
    {"brand": "Honda", "category": "MPV", "doc": "Honda Mobilio 1.5 E CVT 2018 Silver. Odo 72.000 km. Kabin lega, AC double blower, tarikan responsif, siap pakai keluarga.", "price": 145.0},
    {"brand": "Honda", "category": "SUV", "doc": "Honda BR-V 1.5 Prestige with Honda Sensing 2022 Taffeta White. Odo 30.000 km. 7-seater ground clearance 220mm, lane watch camera, nyaman.", "price": 250.0},

    # ==========================================
    # 3. SUZUKI (10 Mobil)
    # ==========================================
    {"brand": "Suzuki", "category": "MPV", "doc": "Suzuki All New Ertiga 1.5 GX AT 2019 Abu-abu Metalik. Odo 56.000 km. Wood panel dashboard, keyless push start, AC digital climate control.", "price": 165.0},
    {"brand": "Suzuki", "category": "MPV", "doc": "Suzuki Ertiga 1.5 Sport AT 2021 Putih Pearl. Odo 42.000 km. Full aero bodykit Suzuki Sport, DRL LED, rear camera, spoiler sporty.", "price": 195.0},
    {"brand": "Suzuki", "category": "MPV", "doc": "Suzuki Ertiga Hybrid GX AT 2022 Silver. Odo 25.000 km. Smart Hybrid ISG hemat bensin, cruise control, auto light with guide me home.", "price": 215.0},
    {"brand": "Suzuki", "category": "SUV", "doc": "Suzuki XL7 Alpha AT 2020 Two Tone Orange Hitam. Odo 48.000 km. Smart e-mirror dashcam depan belakang, roof rail, captain look armrest.", "price": 205.0},
    {"brand": "Suzuki", "category": "SUV", "doc": "Suzuki Jimny 1.5 4x4 AllGrip AT 2021 Kinetic Yellow. Odo 18.000 km. SUV ikonik off-road 4WD, ladder frame kokoh, collector item mulus.", "price": 460.0},
    {"brand": "Suzuki", "category": "Hatchback", "doc": "Suzuki Ignis 1.2 GX AT 2018 Biru Putih. Odo 60.000 km. Urban SUV stylish, push start button, AC auto climate, konsumsi BBM super irit.", "price": 128.0},
    {"brand": "Suzuki", "category": "Hatchback", "doc": "Suzuki Baleno Hatchback 1.5 AT 2020 Merah. Odo 40.000 km. Lampu HID projector, kabin sangat lapang, suspensi empuk ala sedan Eropa.", "price": 175.0},
    {"brand": "Suzuki", "category": "SUV", "doc": "Suzuki Grand Vitara 1.5 Hybrid Ultimate Two Tone 2023 Biru Hitam. Odo 12.000 km. Panoramic sunroof, 360 camera, wireless charger, head-up display.", "price": 340.0},
    {"brand": "Suzuki", "category": "Commercial", "doc": "Suzuki Carry 1.5 Pick Up Flat Deck MT 2019 Putih. Odo 45.000 km. Bak luas 3 sisi buka, mesin K15B tangguh dan irit, siap muatan usaha.", "price": 92.0},
    {"brand": "Suzuki", "category": "City Car", "doc": "Suzuki S-Presso 1.0 MT 2022 Orange. Odo 19.000 km. City car lincah ground clearance 180mm, konsumsi BBM 1:21 km/liter, sangat ekonomis.", "price": 115.0},

    # ==========================================
    # 4. DAIHATSU (9 Mobil)
    # ==========================================
    {"brand": "Daihatsu", "category": "MPV", "doc": "Daihatsu Grand New Xenia 1.3 R MT 2019 Hitam. Odo 55.000 km. AC digital, dual VVT-i, audio steering switch, kamera parkir, orisinil.", "price": 145.0},
    {"brand": "Daihatsu", "category": "MPV", "doc": "Daihatsu All New Xenia 1.5 R CVT ASA 2022 Abu-abu. Odo 28.000 km. Fitur keselamatan aktif ASA (Advanced Safety Assist), transmisi D-CVT responsif.", "price": 205.0},
    {"brand": "Daihatsu", "category": "SUV", "doc": "Daihatsu Terios 1.5 R Deluxe AT 2019 Putih. Odo 58.000 km. Kamera 360 around view monitor, keyless entry, velg two tone 17 inch, 7-seater.", "price": 185.0},
    {"brand": "Daihatsu", "category": "SUV", "doc": "Daihatsu Rocky 1.0 R Turbo CVT ADS 2021 Merah Hitam. Odo 32.000 km. Mesin 1000cc 3 silinder turbo bertenaga, full digital speedometer 7 inch.", "price": 188.0},
    {"brand": "Daihatsu", "category": "LCGC", "doc": "Daihatsu Sigra 1.2 R Deluxe AT 2020 Silver. Odo 46.000 km. Mobil keluarga 7 penumpang ramah kantong, sensor parkir depan belakang, terawat.", "price": 120.0},
    {"brand": "Daihatsu", "category": "LCGC", "doc": "Daihatsu Ayla 1.2 R AT 2021 Kuning. Odo 34.000 km. Spion retract dengan lampu sein, velg polished alloy 14 inch, audio touchscreen.", "price": 128.0},
    {"brand": "Daihatsu", "category": "Hatchback", "doc": "Daihatsu Sirion 1.3 AT Facelift 2019 Biru. Odo 50.000 km. 4 airbags, traction control, sensor sudut depan, kabin fleksibel lapang.", "price": 138.0},
    {"brand": "Daihatsu", "category": "Commercial", "doc": "Daihatsu Gran Max Pick Up 1.5 3W MT 2020 Hitam. Odo 55.000 km. Mesin 1500cc VVT-i bertenaga, bak kokoh tanpa karat, siap cari uang.", "price": 98.0},
    {"brand": "Daihatsu", "category": "Commercial", "doc": "Daihatsu Gran Max Blind Van 1.3 MT 2021 Putih. Odo 40.000 km. Mobil kurir kargo logistik prima, AC dingin, lantai bordes rapi.", "price": 115.0},

    # ==========================================
    # 5. MITSUBISHI (8 Mobil)
    # ==========================================
    {"brand": "Mitsubishi", "category": "MPV", "doc": "Mitsubishi Xpander Ultimate 1.5 AT 2019 Abu-abu. Odo 55.000 km. Keyless entry, cruise control, interior beige mewah, ban tebal.", "price": 205.0},
    {"brand": "Mitsubishi", "category": "MPV", "doc": "Mitsubishi Xpander Facelift Ultimate CVT 2022 Putih Pearl. Odo 30.000 km. Transmisi CVT baru sangat halus, rem electric EPB with auto hold.", "price": 248.0},
    {"brand": "Mitsubishi", "category": "SUV", "doc": "Mitsubishi Xpander Cross 1.5 AT Premium Package 2020 Orange Sunrise. Odo 45.000 km. Jok kulit two-tone, ground clearance 225mm, roof rail.", "price": 228.0},
    {"brand": "Mitsubishi", "category": "SUV", "doc": "Mitsubishi Pajero Sport 2.4 Dakar 4x2 AT 2017 Hitam. Odo 85.000 km. Sunroof, paddle shift, jok kulit elektrik, mesin MIVEC diesel terawat.", "price": 385.0},
    {"brand": "Mitsubishi", "category": "SUV", "doc": "Mitsubishi Pajero Sport 2.4 Dakar Ultimate 4x2 AT 2020 Putih. Odo 50.000 km. Forward collision mitigation, blind spot warning, sunroof.", "price": 465.0},
    {"brand": "Mitsubishi", "category": "SUV", "doc": "Mitsubishi Pajero Sport Dakar 4x4 AT 2019 Abu-abu. Odo 60.000 km. Super Select 4WD-II dengan rear differential lock, audio premium.", "price": 495.0},
    {"brand": "Mitsubishi", "category": "SUV", "doc": "Mitsubishi XFORCE 1.5 Ultimate CVT 2023 Energetic Yellow. Odo 14.000 km. Dynamic Sound Yamaha Premium 8 speaker, drive mode (Gravel, Mud, Wet).", "price": 345.0},
    {"brand": "Mitsubishi", "category": "Commercial", "doc": "Mitsubishi Triton 2.4 DC Ultimate 4x4 AT 2020 Putih. Odo 65.000 km. Double cabin tangguh, mesin 4N15 MIVEC turbo diesel, siap medan berat.", "price": 410.0},

    # ==========================================
    # 6. WULING & EV (8 Mobil)
    # ==========================================
    {"brand": "Wuling", "category": "EV", "doc": "Wuling Air EV Long Range 2022 Avocado Green. Odo 20.000 km. Jarak tempuh 300 km, baterai IP67 tahan banjir, layar ganda 10.25 inch, garansi aktif.", "price": 195.0},
    {"brand": "Wuling", "category": "EV", "doc": "Wuling Air EV Standard Range 2023 Pristine White. Odo 15.000 km. Mobil listrik mungil lincah, bebas ganjil genap Jakarta, charger portable ada.", "price": 160.0},
    {"brand": "Wuling", "category": "EV", "doc": "Wuling Binguo EV 410 km Premium Version 2024 Milk Tea. Odo 8.000 km. Retro modern 5-pintu, dual airbag, cruise control, DC fast charging.", "price": 325.0},
    {"brand": "Wuling", "category": "SUV", "doc": "Wuling Almaz 1.5 RS Pro CVT 2021 Aurora Silver. Odo 40.000 km. Wuling Interconnected Smart Ecosystem (WISE), voice command bahasa Indonesia WIND, sunroof.", "price": 235.0},
    {"brand": "Wuling", "category": "SUV", "doc": "Wuling Alvez 1.5 EX CVT 2023 Tungsten Steel. Odo 18.000 km. Compact SUV modern, electric sunroof, ADAS safety, wireless mirroring.", "price": 210.0},
    {"brand": "Wuling", "category": "MPV", "doc": "Wuling Cortez CT 1.5 Turbo L CVT 2020 Hitam. Odo 52.000 km. Captain seat elektrik, panoramic sunroof, rem cakram 4 roda, sangat lega.", "price": 165.0},
    {"brand": "Wuling", "category": "MPV", "doc": "Wuling Confero S 1.5 L Lux Plus MT 2019 Silver. Odo 65.000 km. MPV 8-seater penggerak roda belakang (RWD), sensor parkir 4 titik, terjangkau.", "price": 105.0},
    {"brand": "BYD", "category": "EV", "doc": "BYD Atto 3 Superior Extended Range 2024 Ski White. Odo 6.000 km. Blade battery aman 500 km range, layar putar 15.6 inch, panoramic roof, ADAS.", "price": 475.0},

    # ==========================================
    # 7. NISSAN (6 Mobil)
    # ==========================================
    {"brand": "Nissan", "category": "MPV", "doc": "Nissan Grand Livina 1.5 Highway Star AT 2016 Putih. Odo 78.000 km. Jok kulit beige, TV plafon, suspensi sedan monokok sangat nyaman.", "price": 115.0},
    {"brand": "Nissan", "category": "MPV", "doc": "Nissan Serena 2.0 Highway Star C26 AT 2017 Hitam. Odo 68.000 km. Dual power sliding door dengan sensor kaki, panoramic glass roof, meja lipat.", "price": 215.0},
    {"brand": "Nissan", "category": "MPV", "doc": "Nissan Serena 2.0 Highway Star C27 AT 2019 Putih Two Tone. Odo 45.000 km. Desain V-Motion modern, 7 USB charging port, cruise control, super nyaman.", "price": 315.0},
    {"brand": "Nissan", "category": "SUV", "doc": "Nissan X-Trail 2.5 T32 CVT 2016 Silver Metalik. Odo 72.000 km. Around View Monitor 360 kamera, hands-free touchless backdoor, kursi zero gravity.", "price": 185.0},
    {"brand": "Nissan", "category": "SUV", "doc": "Nissan Kicks e-Power 1.2 AT 2021 Monarch Orange. Odo 35.000 km. Mobil sensasi 100% elektrik tanpa perlu colok cas listrik (bensin jadi genset).", "price": 320.0},
    {"brand": "Nissan", "category": "Hatchback", "doc": "Nissan March 1.2 AT 2017 Merah Metalik. Odo 55.000 km. AC digital bulat ikonik, radius putar kecil 4.5m sangat lincah di kemacetan.", "price": 108.0},

    # ==========================================
    # 8. HYUNDAI (7 Mobil)
    # ==========================================
    {"brand": "Hyundai", "category": "EV", "doc": "Hyundai Ioniq 5 Signature Long Range 2022 Gravity Gold. Odo 28.000 km. Baterai SOH 99%, ADAS SmartSense lengkap, V2L port siap jalan.", "price": 575.0},
    {"brand": "Hyundai", "category": "SUV", "doc": "Hyundai Creta 1.5 Prime Two Tone AT 2022 Putih Atap Hitam. Odo 30.000 km. Panoramic sunroof, BOSE audio, ventilated seats, Bluelink aktif.", "price": 305.0},
    {"brand": "Hyundai", "category": "SUV", "doc": "Hyundai Palisade 2.2 D Signature AWD 2021 Putih. Odo 38.000 km. 7-seater captain seat, dual sunroof, Nappa leather, mesin diesel bertenaga.", "price": 750.0},
    {"brand": "Hyundai", "category": "MPV", "doc": "Hyundai Stargazer 1.5 Prime AT 2022 Mangrove Brown. Odo 26.000 km. Ambient cabin light, captain seat with table, Hyundai SmartSense, wireless charging.", "price": 225.0},
    {"brand": "Hyundai", "category": "SUV", "doc": "Hyundai Santa Fe 2.2 Diesel Signature 8-DCT 2021 Hitam. Odo 40.000 km. Mesin Smartstream D2.2 bertenaga 202 PS, panoramic roof, blind spot view monitor.", "price": 560.0},
    {"brand": "Hyundai", "category": "MPV", "doc": "Hyundai Staria 2.2 Diesel Signature 9 2022 Hitam. Odo 32.000 km. Desain pesawat luar angkasa futuristik, kursi putar 180 derajat, audio BOSE.", "price": 790.0},
    {"brand": "Hyundai", "category": "EV", "doc": "Hyundai Ioniq 6 Signature AWD 2023 Abyss Black. Odo 10.000 km. Electrified streamliner aerodinamis, jarak tempuh 519 km, acceleration 0-100 5.1s.", "price": 960.0},

    # ==========================================
    # 9. MAZDA (8 Mobil)
    # ==========================================
    {"brand": "Mazda", "category": "Hatchback", "doc": "Mazda 2 1.5 GT SkyActiv AT 2018 Soul Red Crystal. Odo 52.000 km. Head-up display, paddle shift, blind spot monitoring, cat mulus orisinil.", "price": 190.0},
    {"brand": "Mazda", "category": "Hatchback", "doc": "Mazda 3 Hatchback 2.0 SkyActiv-G 2020 Poly Metal Grey. Odo 35.000 km. BOSE sound system 12 speakers, radar cruise control, interior mewah.", "price": 395.0},
    {"brand": "Mazda", "category": "Sedan", "doc": "Mazda 6 Sedan 2.5 SkyActiv Elite 2019 Snowflake White. Odo 42.000 km. Nappa leather warna cokelat oriental, sun roof, 360 kamera, kemewahan Jepang.", "price": 430.0},
    {"brand": "Mazda", "category": "SUV", "doc": "Mazda CX-3 1.5 Sport AT 2021 Snowflake White. Odo 33.000 km. Mesin 1500cc hemat dan lincah, wireless Apple CarPlay, 6 airbag, mulus.", "price": 275.0},
    {"brand": "Mazda", "category": "SUV", "doc": "Mazda CX-5 2.5 Elite AT 2019 Machine Grey. Odo 48.000 km. Sunroof, BOSE audio, hands-free power tailgate, kursi kulit ventilasi.", "price": 355.0},
    {"brand": "Mazda", "category": "SUV", "doc": "Mazda CX-5 2.5 Kuro Edition AWD 2022 Zircon Sand. Odo 24.000 km. Penggerak i-Activ AWD, aksen hitam gloss velg dan spion, merah stitching.", "price": 490.0},
    {"brand": "Mazda", "category": "SUV", "doc": "Mazda CX-8 2.5 Elite AT 2020 Deep Crystal Blue. Odo 40.000 km. SUV 6-seater captain seat dengan konsol tengah mewah, kabin ultra senyap.", "price": 540.0},
    {"brand": "Mazda", "category": "SUV", "doc": "Mazda CX-9 2.5 Turbo AWD 2019 Jet Black. Odo 50.000 km. Mesin 2500cc SkyActiv Turbo 231 PS, sunroof, audio premium BOSE, velg 20 inch.", "price": 580.0},

    # ==========================================
    # 10. BMW (9 Mobil)
    # ==========================================
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 320i F30 LCI Sport N20 2016 Putih Interior Merah. Odo 65.000 km. Lampu LED LCI asli, iDrive besar, transmisi 8-speed ZF prima.", "price": 310.0},
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 330i G20 M Sport 2020 Portimao Blue. Odo 32.000 km. BMW Live Cockpit Professional, Laserlight, Harman Kardon audio, garansi BSI.", "price": 720.0},
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 320i G20 Sport 2020 Mineral White. Odo 38.000 km. Reversing assistant otomatis mundur 50m, ambient light, Apple CarPlay wireless.", "price": 630.0},
    {"brand": "BMW", "category": "SUV", "doc": "BMW X1 sDrive18i xLine F48 2018 Hitam. Odo 54.000 km. Panoramic sunroof, electric seat with memory, bagasi luas, ban RFT tebal.", "price": 360.0},
    {"brand": "BMW", "category": "SUV", "doc": "BMW X3 sDrive20i xLine G01 2019 Phycic Blue. Odo 42.000 km. Panorama glass roof, gesture control iDrive, comfort access, ban RFT Pirelli.", "price": 620.0},
    {"brand": "BMW", "category": "SUV", "doc": "BMW X5 xDrive40i xLine G05 2020 Carbon Black. Odo 35.000 km. 7-seater, air suspension adaptif, Laserlight, audio Harman Kardon surround.", "price": 1150.0},
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 520i G30 Luxury Line 2018 Hitam. Odo 45.000 km. Display key, ambient light 11 warna, kabin sangat senyap, rawatan Eurokars.", "price": 550.0},
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 530i G30 M Sport 2019 Bluestone Metalik. Odo 36.000 km. Sunroof, M Aerodynamics package, velg 19 M, rem M Sport biru, full original.", "price": 690.0},
    {"brand": "BMW", "category": "Sedan", "doc": "BMW 218i Gran Coupe M Sport 2022 Snapper Rocks Blue. Odo 20.000 km. Desain coupe 4-pintu seksi, frameless door, transmisi dual clutch 7-speed.", "price": 540.0},

    # ==========================================
    # 11. MERCEDES-BENZ (8 Mobil)
    # ==========================================
    {"brand": "Mercedes-Benz", "category": "Sedan", "doc": "Mercedes-Benz C200 W205 Avantgarde 2016 Silver. Odo 60.000 km. Agility control, touchpad iDrive, interior artico leather mulus.", "price": 340.0},
    {"brand": "Mercedes-Benz", "category": "Sedan", "doc": "Mercedes-Benz C300 W205 AMG Line 2018 Putih. Odo 42.000 km. Panoramic roof, Burmester surround sound, velg 19 AMG, super terawat.", "price": 520.0},
    {"brand": "Mercedes-Benz", "category": "Sedan", "doc": "Mercedes-Benz E300 W213 Exclusive 2017 Hitam. Odo 50.000 km. Widescreen cockpit dual 12.3 inch, air suspension, kursi pijat depan.", "price": 590.0},
    {"brand": "Mercedes-Benz", "category": "Hatchback", "doc": "Mercedes-Benz A200 Progressive Line W177 2019 Denim Blue. Odo 35.000 km. Hey Mercedes MBUX voice assistant, dual screen cockpit, ambient light 64 warna.", "price": 460.0},
    {"brand": "Mercedes-Benz", "category": "SUV", "doc": "Mercedes-Benz GLA 200 AMG Line H247 2021 Iridium Silver. Odo 28.000 km. Compact luxury SUV, panoramic roof, AMG body styling, velg 19.", "price": 610.0},
    {"brand": "Mercedes-Benz", "category": "SUV", "doc": "Mercedes-Benz GLC 200 AMG Line X253 Facelift 2020 Selenite Grey. Odo 36.000 km. MBUX touch screen, panoramic roof, power tailgate, Burmester.", "price": 720.0},
    {"brand": "Mercedes-Benz", "category": "SUV", "doc": "Mercedes-Benz GLB 200 Progressive Line 7-Seater 2021 Polar White. Odo 30.000 km. SUV mewah 7 penumpang, panoramic sliding roof, praktis.", "price": 680.0},
    {"brand": "Mercedes-Benz", "category": "Sedan", "doc": "Mercedes-Benz CLA 200 AMG Line C118 2020 Mountain Grey. Odo 26.000 km. 4-door coupe frameless, interior sporty dual-tone red black, LED High Performance.", "price": 640.0},

    # ==========================================
    # 12. LAINNYA: KIA, ISUZU, FORD, BYD (8 Mobil)
    # ==========================================
    {"brand": "Kia", "category": "SUV", "doc": "Kia Sonet 1.5 Premiere iVT 2021 Clear White. Odo 35.000 km. Sunroof, BOSE sound system, ventilated front seats, remote engine start, wireless charger.", "price": 215.0},
    {"brand": "Kia", "category": "SUV", "doc": "Kia Seltos 1.4 Turbo GT Line 2021 Glacier White Pearl. Odo 38.000 km. Mesin 1400cc Turbo 140 PS, transmisi 7-DCT, head-up display, sunroof.", "price": 265.0},
    {"brand": "Kia", "category": "MPV", "doc": "Kia Grand Carnival 2.2 Diesel Premiere 2022 Hitam. Odo 28.000 km. 11-seater mewah, dual sunroof, smart power sliding door, mesin diesel bertenaga.", "price": 680.0},
    {"brand": "Isuzu", "category": "MPV", "doc": "Isuzu Panther Grand Touring 2.5 Turbo Diesel MT 2016 Hitam. Odo 90.000 km. Mesin 4JA1 legendaris badak dan tahan banting, AC dingin, siap segala medan.", "price": 175.0},
    {"brand": "Isuzu", "category": "SUV", "doc": "Isuzu MU-X 1.9 4x4 AT 2022 Splash White. Odo 35.000 km. Mesin RZ4E Blue Power diesel irit tangguh, rough terrain mode, penggerak 4WD sejati.", "price": 440.0},
    {"brand": "Ford", "category": "SUV", "doc": "Ford Everest 2.0 Bi-Turbo Titanium 4x4 AT 2023 Alabaster White. Odo 20.000 km. Mesin diesel 210 PS 500 Nm, transmisi 10-speed, panoramic roof, Matrix LED.", "price": 780.0},
    {"brand": "Ford", "category": "Commercial", "doc": "Ford Ranger 2.0 Bi-Turbo Wildtrak 4x4 AT 2023 Absolute Black. Odo 22.000 km. Double cabin premium, layar vertikal 12 inch SYNC 4A, roller shutter elektrik.", "price": 650.0},
    {"brand": "BYD", "category": "EV", "doc": "BYD Seal Performance AWD 2024 Aurora White. Odo 5.000 km. 523 HP dual motor 0-100 km/h dalam 3.8 detik, Head-up display, Dynaudio 12 speaker.", "price": 675.0},
]


def seed_database():
    print(f"📦 Menginisialisasi ChromaDB di folder '{DB_PATH}'...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="cars")

    print(f"🧠 Memuat Model Embedding: 'sentence-transformers/all-MiniLM-L6-v2'...")
    encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    documents = [c["doc"] for c in SAMPLE_CARS_DATASET]
    metadatas = [{"brand": c["brand"], "category": c["category"], "price": float(c["price"])} for c in SAMPLE_CARS_DATASET]
    ids = [f"car_{i:04d}" for i in range(len(SAMPLE_CARS_DATASET))]

    print(f"⚡ Menghitung Vektor Embedding untuk {len(documents)} data mobil...")
    embeddings = encoder.encode(documents, show_progress_bar=True).tolist()

    print(f"💾 Menyimpan dataset baru ke ChromaDB (upserting)...")
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"✅ Selesai! Database ChromaDB berhasil diperluas menjadi {collection.count()} mobil.")


if __name__ == "__main__":
    seed_database()
