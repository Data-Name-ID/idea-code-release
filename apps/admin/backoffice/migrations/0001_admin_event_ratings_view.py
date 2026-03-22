from django.db import migrations

CREATE_VIEW_SQL = """
CREATE OR REPLACE VIEW admin_event_ratings AS
SELECT
    CONCAT(event_id::text, ':', user_id::text) AS id,
    event_id,
    user_id,
    team_id,
    status,
    place,
    awarded_at
FROM event_ratings;
"""

DROP_VIEW_SQL = """
DROP VIEW IF EXISTS admin_event_ratings;
"""


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=CREATE_VIEW_SQL,
            reverse_sql=DROP_VIEW_SQL,
        ),
    ]
