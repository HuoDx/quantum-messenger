class Notification:
    TEXT = 1
    HTML = 2
    MARKDOWN = 3
    def __init__(self, content, notification_type, summary):
        if notification_type not in [Notification.TEXT, Notification.HTML, Notification.MARKDOWN]:
            raise Exception('Invalid notification type.')
        self.content = content
        self._type = notification_type
        self.summary = summary
        