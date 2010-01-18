table = 'django_admin_log'
fields = ['id', 'action_time', 'user_id', 'content_type_id', 'object_id', 'object_repr', 'action_flag', 'change_message']
#default item format: "fieldname":("type", "value")
default = {}
records = [
[1, '2009-12-02 17:57:31', 1, 8, u'1', u'Factor object', 1, u'']
[2, '2009-12-02 17:58:07', 1, 8, u'1', u'Factor object', 2, u'Added answer "Answer object".']
[3, '2009-12-02 17:58:37', 1, 8, u'1', u'Factor object', 2, u'Added answer "Answer object".']
[4, '2009-12-02 17:59:31', 1, 8, u'1', u'Factor object', 2, u'Added answer "Answer object". Added answer "Answer object". Added answer "Answer object".']
[5, '2009-12-02 18:01:49', 1, 8, u'2', u'Factor object', 1, u'']
[6, '2009-12-02 18:02:18', 1, 8, u'2', u'Factor object', 2, u'Added answer "Answer object". Added answer "Answer object".']
[7, '2009-12-02 19:27:44', 1, 8, u'2', u'Factor object', 2, u'Changed info_heading and info_text for answer "Answer object". Changed info_heading and info_text for answer "Answer object". Changed info_heading and info_text for answer "Answer object". Changed info_heading and info_text for answer "Answer object".']
[8, '2009-12-02 19:28:52', 1, 8, u'1', u'Factor object', 2, u'Changed info_heading for answer "Answer object". Changed info_heading for answer "Answer object". Changed info_heading for answer "Answer object". Changed info_heading for answer "Answer object". Changed info_heading for answer "Answer object".']
[9, '2009-12-02 19:29:55', 1, 8, u'1', u'Factor object', 2, u'Changed info_text for answer "Answer object". Changed info_text for answer "Answer object". Changed info_text for answer "Answer object". Changed info_text for answer "Answer object". Changed info_text for answer "Answer object".']
[10, '2009-12-02 19:32:40', 1, 8, u'3', u'Factor object', 1, u'']
[11, '2010-01-16 23:59:30', 1, 11, u'1', u'Technology object', 1, u'']
[12, '2010-01-17 00:05:39', 1, 11, u'2', u'Jerry can', 1, u'']
[13, '2010-01-17 05:02:49', 1, 11, u'2', u'Jerry can', 3, u'']
[14, '2010-01-17 05:03:03', 1, 11, u'1', u'Sewer discharge station', 3, u'']
]
