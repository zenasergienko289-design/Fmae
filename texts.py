# Premium-эмодзи для валют
EMOJI_STARS = "5406812184359507637"
EMOJI_TON = "5048883070338336640"


def currency_html(code: str) -> str:
    if code == "GRAM":
        return f'<tg-emoji emoji-id="{EMOJI_TON}">💎</tg-emoji> TON'
    return f'<tg-emoji emoji-id="{EMOJI_STARS}">⭐</tg-emoji> Stars'


TEXTS = {
    "ru": {
        "offer": (
            "Пользователь предлагает Вам\n"
            "<b>{amount} {currency}</b> за подарок <b>{gift_name}</b>.\n\n"
            "Предложение действует ещё <b>{time_left}</b>."
        ),
        "deal": (
            "Заказ <b>#TG-{order_id}</b>\n\n"
            "Покупатель зарезервировал <b>{amount} {currency}</b> через гарантийную систему Telegram. "
            "Средства находятся на специальном счёте удержания и будут автоматически начислены "
            "на ваш баланс сразу после передачи подарка.\n\n"
            "Инструкция для завершения сделки:\n"
            "1. Передайте пользователю: <b>@{gift_username}</b>\n"
            "2. Нажмите «Передать подарок» и выберите <b>{gift_name}</b>\n"
            "3. Подтвердите передачу подарка.\n\n"
            "Система Telegram зафиксирует транзакцию и моментально зачислит <b>{amount} {currency}</b> "
            "на ваш баланс. Резерв действует ещё <b>{time_left}</b>."
        ),
        "btn_accept": "Принять",
        "btn_decline": "Отклонить",
        "btn_give": "Передать подарок",
        "btn_confirm": "Подтвердить передачу",
        "declined": "Вы отклонили предложение.",
        "confirm_msg": (
            "❌ Подарок передан не был.\n"
            "Транзакция отменена. Средства возвращены покупателю."
        ),
        "expired": "⌛ Время сделки истекло.",
        "not_found": "Сделка не найдена",
    },
    "en": {
        "offer": (
            "A user offers you\n"
            "<b>{amount} {currency}</b> for the gift <b>{gift_name}</b>.\n\n"
            "Offer valid for <b>{time_left}</b>."
        ),
        "deal": (
            "Order <b>#TG-{order_id}</b>\n\n"
            "The buyer has reserved <b>{amount} {currency}</b> through Telegram's escrow system. "
            "The funds are held in a special escrow account and will be automatically credited "
            "to your balance right after the gift is transferred.\n\n"
            "Instructions to complete the deal:\n"
            "1. Transfer to user: <b>@{gift_username}</b>\n"
            "2. Click «Transfer gift» and select <b>{gift_name}</b>\n"
            "3. Confirm the gift transfer.\n\n"
            "Telegram will record the transaction and instantly credit <b>{amount} {currency}</b> "
            "to your balance. The reservation is valid for <b>{time_left}</b>."
        ),
        "btn_accept": "Accept",
        "btn_decline": "Decline",
        "btn_give": "Transfer gift",
        "btn_confirm": "Confirm transfer",
        "declined": "You declined the offer.",
        "confirm_msg": (
            "❌ The gift was not transferred.\n"
            "Transaction cancelled. Funds returned to the buyer."
        ),
        "expired": "⌛ Deal time expired.",
        "not_found": "Deal not found",
    },
    "cn": {
        "offer": (
            "有用户向您提议\n"
            "以 <b>{amount} {currency}</b> 购买礼物 <b>{gift_name}</b>。\n\n"
            "报价有效期还剩 <b>{time_left}</b>。"
        ),
        "deal": (
            "订单 <b>#TG-{order_id}</b>\n\n"
            "买家已通过 Telegram 担保系统预留了 <b>{amount} {currency}</b>。"
            "资金存放在专用托管账户中，礼物转移后将自动记入您的余额。\n\n"
            "完成交易的说明：\n"
            "1. 转移给用户：<b>@{gift_username}</b>\n"
            "2. 点击 «转移礼物» 并选择 <b>{gift_name}</b>\n"
            "3. 确认礼物转移。\n\n"
            "Telegram 将记录交易并立即将 <b>{amount} {currency}</b> 记入您的余额。"
            "预留有效期还剩 <b>{time_left}</b>。"
        ),
        "btn_accept": "接受",
        "btn_decline": "拒绝",
        "btn_give": "转移礼物",
        "btn_confirm": "确认转移",
        "declined": "您拒绝了该报价。",
        "confirm_msg": (
            "❌ 礼物未被转移。\n"
            "交易已取消。资金已退还给买家。"
        ),
        "expired": "⌛ 交易时间已到。",
        "not_found": "未找到交易",
    },
    "ar": {
        "offer": (
            "يعرض عليك المستخدم\n"
            "<b>{amount} {currency}</b> مقابل الهدية <b>{gift_name}</b>.\n\n"
            "العرض صالح لمدة <b>{time_left}</b>."
        ),
        "deal": (
            "الطلب <b>#TG-{order_id}</b>\n\n"
            "قام المشتري بحجز <b>{amount} {currency}</b> عبر نظام الضمان في تيليجرام. "
            "يتم الاحتفاظ بالأموال في حساب ضمان خاص وسيتم إضافتها تلقائيًا "
            "إلى رصيدك بمجرد نقل الهدية.\n\n"
            "تعليمات لإتمام الصفقة:\n"
            "1. انقل إلى المستخدم: <b>@{gift_username}</b>\n"
            "2. اضغط على «نقل الهدية» واختر <b>{gift_name}</b>\n"
            "3. أكد نقل الهدية.\n\n"
            "سيسجل تيليجرام المعاملة ويضيف <b>{amount} {currency}</b> "
            "فورًا إلى رصيدك. الحجز صالح لمدة <b>{time_left}</b>."
        ),
        "btn_accept": "قبول",
        "btn_decline": "رفض",
        "btn_give": "نقل الهدية",
        "btn_confirm": "تأكيد النقل",
        "declined": "لقد رفضت العرض.",
        "confirm_msg": (
            "❌ لم يتم نقل الهدية.\n"
            "تم إلغاء المعاملة. تم إرجاع الأموال إلى المشتري."
        ),
        "expired": "⌛ انتهى وقت الصفقة.",
        "not_found": "لم يتم العثور على الصفقة",
    },
}
