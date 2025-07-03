package com.example.analizardeimagenesonline

data class CattleInfo(
    val name: String,
    val description: String,
    val averageWeightKg: String,
    val averageHeightCm: String,
    val originCountry: String,
    val coatColor: String,
    val hornStatus: String,
    val temperament: String,
    val purpose: String,
    val climateAdaptability: String
)

val LABELS = listOf(
    "Ankole",
    "Belted Galloway",
    "Brahman",
    "Desconocido",
    "Frisona",
    "Highland"
)

val cattleDetails = mapOf(
    "Ankole" to CattleInfo(
        name = "Ankole",
        description = "Raza africana (Ankole-Watusi) famosa por sus cuernos exageradamente largos.",
        averageWeightKg = "450–700 kg",
        averageHeightCm = "140–160 cm",
        originCountry = "Uganda / Ruanda",
        coatColor = "Rojo, moteado o jaspeado",
        hornStatus = "Con cuernos muy largos y curvados",
        temperament = "Dócil pero alerta",
        purpose = "Carne y leche",
        climateAdaptability = "Excelente resistencia al calor"
    ),
    "Belted Galloway" to CattleInfo(
        name = "Belted Galloway",
        description = "Raza escocesa reconocible por su franja blanca en el cuerpo, valorada por su carne magra.",
        averageWeightKg = "450–850 kg",
        averageHeightCm = "120–135 cm",
        originCountry = "Escocia",
        coatColor = "Negro con franja blanca (también rojo y dun)",
        hornStatus = "Sin cuernos",
        temperament = "Tranquilo y resistente",
        purpose = "Carne",
        climateAdaptability = "Excelente tolerancia al frío y humedad"
    ),
    "Brahman" to CattleInfo(
        name = "Brahman",
        description = "Raza india resistente al calor, con joroba y orejas largas, común en cruzamientos.",
        averageWeightKg = "500–1000 kg",
        averageHeightCm = "135–150 cm",
        originCountry = "India (desarrollada en EE.UU.)",
        coatColor = "Gris claro, blanco o rojo",
        hornStatus = "Con cuernos (a veces despuntados)",
        temperament = "Alerta, inteligente",
        purpose = "Carne y cruzamiento",
        climateAdaptability = "Excelente resistencia al calor y parásitos"
    ),
    "Desconocido" to CattleInfo(
        name = "Desconocido",
        description = "La raza del ganado no pudo ser determinada con certeza.",
        averageWeightKg = "-",
        averageHeightCm = "-",
        originCountry = "-",
        coatColor = "-",
        hornStatus = "-",
        temperament = "-",
        purpose = "-",
        climateAdaptability = "-"
    ),
    "Frisona" to CattleInfo(
        name = "Frisona",
        description = "Raza holandesa (Holstein Friesian) muy extendida por su alta producción de leche.",
        averageWeightKg = "600–750 kg",
        averageHeightCm = "140–160 cm",
        originCountry = "Países Bajos",
        coatColor = "Blanco y negro (mármol)",
        hornStatus = "Pequeños cuernos o descornada",
        temperament = "Tranquila y dócil",
        purpose = "Leche",
        climateAdaptability = "Buena en climas templados"
    ),
    "Highland" to CattleInfo(
        name = "Highland",
        description = "Raza escocesa antigua de pelaje largo y cuernos prominentes, adaptada a climas fríos.",
        averageWeightKg = "500–800 kg",
        averageHeightCm = "110–130 cm",
        originCountry = "Escocia",
        coatColor = "Rojo, negro, amarillo, blanco",
        hornStatus = "Con cuernos largos",
        temperament = "Tranquilo pero fuerte",
        purpose = "Carne (ecológica)",
        climateAdaptability = "Excelente en climas fríos y húmedos"
    )
)
