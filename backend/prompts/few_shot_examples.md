# Few-Shot Examples for LLM Prompts

These examples help improve LLM accuracy for receipt parsing.

## Example 1: Simple Receipt (Russian)

**Raw OCR Text:**
```
ООО "Рога и Копыта"
ИНН 1234567890
12.03.2025
Товары/Услуги:
Канцтовары - 3450.00
Итого: 3450.00 RUB
Оплата: Карта
```

**Expected JSON:**
```json
{
  "vendor": "ООО Рога и Копыта",
  "date": "2025-03-12",
  "total": 3450.00,
  "currency": "RUB",
  "items": [
    {"name": "Канцтовары", "qty": 1, "price": 3450.00}
  ],
  "tax_id": "1234567890",
  "payment_method": "Карта",
  "raw_confidence": "high",
  "notes": null
}
```

## Example 2: Incomplete Receipt (Poor OCR)

**Raw OCR Text:**
```
MaгaзиH
12.0З.2О25
Сyммa: 15OO р.
```

**Expected JSON:**
```json
{
  "vendor": "Магазин",
  "date": "2025-03-12",
  "total": 1500.0,
  "currency": "RUB",
  "items": [],
  "tax_id": null,
  "payment_method": null,
  "raw_confidence": "low",
  "notes": "Poor OCR quality, many character recognition errors"
}
```

## Example 3: Bank Transaction Screenshot

**Raw OCR Text:**
```
Перевод
Получатель: ИП Иванов
Сумма: 5000 ₽
Дата: 15.03.2025
Комиссия: 0 ₽
```

**Expected JSON:**
```json
{
  "vendor": "ИП Иванов",
  "date": "2025-03-15",
  "total": 5000.0,
  "currency": "RUB",
  "items": [],
  "tax_id": null,
  "payment_method": "Перевод",
  "raw_confidence": "medium",
  "notes": "Bank transfer screenshot, not a formal receipt"
}
```

## Example 4: Detailed Receipt with Multiple Items

**Raw OCR Text:**
```
ООО "КанцТорг"
Москва, ул. Ленина, 10
ИНН 9876543210
15.03.2025

Наименование       Кол.  Цена    Сумма
Ручка синяя         10   25.00   250.00
Бумага А4           5    350.00  1750.00
Степлер             2    180.00  360.00

Итого:                           2360.00 RUB
Оплата: Безналичный расчет
```

**Expected JSON:**
```json
{
  "vendor": "ООО КанцТорг",
  "date": "2025-03-15",
  "total": 2360.0,
  "currency": "RUB",
  "items": [
    {"name": "Ручка синяя", "qty": 10, "price": 25.0},
    {"name": "Бумага А4", "qty": 5, "price": 350.0},
    {"name": "Степлер", "qty": 2, "price": 180.0}
  ],
  "tax_id": "9876543210",
  "payment_method": "Безналичный расчет",
  "raw_confidence": "high",
  "notes": null
}
```

## Example 5: Medical Receipt

**Raw OCR Text:**
```
Медицинский центр "Здоровье"
ИНН 1122334455
20.03.2025

Услуга: Консультация терапевта
Стоимость: 2500.00 руб.

Пациент: Иванов И.И.
Оплачено: Наличные
```

**Expected JSON:**
```json
{
  "vendor": "Медицинский центр Здоровье",
  "date": "2025-03-20",
  "total": 2500.0,
  "currency": "RUB",
  "items": [
    {"name": "Консультация терапевта", "qty": 1, "price": 2500.0}
  ],
  "tax_id": "1122334455",
  "payment_method": "Наличные",
  "raw_confidence": "high",
  "notes": "Medical service receipt"
}
```

## Example 6: Empty/Failed OCR

**Raw OCR Text:**
```
[Image appears to be too blurry to read]
```

**Expected JSON:**
```json
{
  "vendor": null,
  "date": null,
  "total": null,
  "currency": null,
  "items": [],
  "tax_id": null,
  "payment_method": null,
  "raw_confidence": "low",
  "notes": "OCR failed - image quality too poor"
}
```

---

## Classification Examples

### Example 1: Office Supplies
**Receipt Data:**
```json
{
  "vendor": "ООО КанцТорг",
  "total": 2360.0,
  "items": [{"name": "Ручка синяя"}, {"name": "Бумага А4"}]
}
```

**Classification:**
```json
{
  "category": "канцтовары",
  "tax_deduction_possible": "yes",
  "reasoning_short": "Канцелярские товары для офиса могут быть отнесены на расходы компании. Требуется накладная и счет-фактура.",
  "required_documents": ["Чек", "Накладная", "Счет-фактура"]
}
```

### Example 2: Medical Services
**Receipt Data:**
```json
{
  "vendor": "Медицинский центр Здоровье",
  "total": 2500.0,
  "items": [{"name": "Консультация терапевта"}]
}
```

**Classification:**
```json
{
  "category": "медицинские",
  "tax_deduction_possible": "yes",
  "reasoning_short": "Медицинские услуги могут быть включены в налоговый вычет при наличии лицензии медучреждения и подтверждающих документов.",
  "required_documents": ["Чек", "Договор", "Копия лицензии медучреждения", "Справка об оплате медуслуг"]
}
```

### Example 3: Unknown Category
**Receipt Data:**
```json
{
  "vendor": "Магазин",
  "total": 1500.0,
  "items": []
}
```

**Classification:**
```json
{
  "category": "прочее",
  "tax_deduction_possible": "maybe",
  "reasoning_short": "Недостаточно информации для точной классификации. Требуется уточнение характера покупки.",
  "required_documents": ["Чек", "Служебная записка с описанием цели покупки"]
}
```
