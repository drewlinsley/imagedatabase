#!/usr/bin/env python
import sshtunnel
import itertools
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from settings import credentials
from settings.db_config import config as db_config
sshtunnel.DAEMON = True  # Prevent hanging process due to forward thread


def flatten(x):
    return list(itertools.chain(*x))


class db(object):
    def __init__(self, config):
        # Pass config -> this class
        for k, v in config.items():
            setattr(self, k, v)

    def __enter__(self):
        forward = sshtunnel.SSHTunnelForwarder(
            credentials.x7_credentials()['ssh_address'],
            ssh_username=self.user,
            ssh_password=self.password,
            remote_bind_address=('127.0.0.1', 5432))
        forward.start()
        pgsql_port = forward.local_bind_port
        pgsql_string = credentials.postgresql_connection(str(pgsql_port))
        self.forward = forward
        self.pgsql_port = pgsql_port
        self.pgsql_string = pgsql_string
        self.conn = psycopg2.connect(**pgsql_string)
        self.conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.forward.close()
        if exc_type is not None:
            print exc_type, exc_value, traceback
        return self

    def close_db(self):
        self.cur.close()
        self.conn.close()

    def init_db(self):
        db_schema = open(self.db_schema_file).read().splitlines()
        for s in db_schema:
            t = s.strip()
            if len(t):
                self.cur.execute(t)
        # self.cur.execute(open(self.db_schema_file).read())
        self.conn.commit()

    def return_status(
            self,
            label,
            throw_error=False):
        """
        General error handling and status of operations.
        ::
        label: a string of the SQL operation (e.g. 'INSERT').
        throw_error: if you'd like to terminate execution if an error.
        """
        if label in self.cur.statusmessage:
            print 'Successful %s.' % label
        else:
            if throw_error:
                raise RuntimeError('%s' % self.cur.statusmessag)
            else:
                'Encountered error during %s: %s.' % (
                    label, self.cur.statusmessage
                    )

    def add_experiment(
            self,
            experiment_name,
            parent_experiment=None,
            status_message=False):
        """
        For adding a new experiment name, such as ILSVRC12
        ::
        experiment_name: name of experiment to add
        parent_experiment: linking a child (e.g. clickme) -> parent (ILSVRC12)
        """
        if parent_experiment is not None:
            self.cur.execute(
                """
                SELECT * FROM experiments WHERE name=%(experiment_name)s;
                """,
                {
                    'experiment_name': experiment_name
                }
                )
            parent_id = self.cur.fetchone()['_id']
        else:
            parent_id = None
        self.cur.execute(
            """
            INSERT INTO experiments
            (name, parent_exp_id)
            SELECT %(experiment_name)s, %(parent_exp_id)s
            WHERE NOT EXISTS (
                SELECT 1 FROM experiments WHERE name=%(experiment_name)s
                )
            RETURNING _id;
            """,
            {
                'experiment_name': experiment_name,
                'parent_exp_id': parent_id,
            }
            )
        if status_message:
            self.return_status('INSERT')
        output = self.cur.fetchone()
        if output:
            return output['_id']
        else:
            self.cur.execute(
                """
                SELECT _id from experiments
                WHERE name=%(experiment_name)s
                """,
                {
                    'experiment_name': experiment_name,
                    'parent_exp_id': parent_id,
                }
            )
            return self.cur.fetchone()['_id']

    def add_labels(
            self,
            name,
            experiment_id,
            class_index,
            parent_label_id=None,
            status_message=False):
        """
        For adding a new experiment name, such as ILSVRC12
        ::
        name: label string e.g. n210302 for synset
        experiment_id: _id of the experiment
        class_index: e.g. synset category index
        parent_label_id: e.g. the heatmap for an image
        """
        self.cur.execute(
            """
            INSERT INTO labels
            (name, experiment_id, class_index, parent_label_id)
            SELECT %(name)s, %(experiment_id)s, %(class_index)s, %(parent_label_id)s
            WHERE NOT EXISTS (
                SELECT * FROM labels
                WHERE name=%(name)s AND experiment_id=%(experiment_id)s
                )
            """,
            {
                'name': name,
                'experiment_id': experiment_id,
                'class_index': class_index,
                'parent_label_id': parent_label_id
            }
            )
        if status_message:
            self.return_status('INSERT')

    def add_images(
            self,
            filename,
            encoding,
            height,
            width,
            experiment_id,
            parent_image_id,
            channels=1,
            status_message=False):
        self.cur.execute(
            """
            INSERT INTO images
            (filename, encoding, height, width, channels, experiment_id, parent_image_id)
            VALUES (%(filename)s, %(encoding)s, %(height)s, %(width)s, %(channels)s, %(experiment_id)s, %(parent_image_id)s)
            RETURNING _id""",
            {
                'filename': filename,
                'encoding': encoding,
                'height': height,
                'width': width,
                'channels': channels,
                'experiment_id': experiment_id,
                'parent_image_id': parent_image_id,
            }
            )

        if status_message:
            self.return_status('INSERT')
        return self.cur.fetchone()['_id']

    def add_image_label_join(
            self,
            filename,
            image_experiment_name,
            label_name,
            label_experiment_name,
            label_order=None,
            status_message=False):
        """
        image_experiment_name e.g. imagenet
        label_experiment_name e.g. animal non animal
        label_name e.g. synset
        label_order e.g. the ordering of images in a specific db or experiment
        """
        self.cur.execute(
            """
            INSERT INTO image_label_join
            (image_id, label_id, image_order)
            VALUES (
                (SELECT _id FROM images
                    WHERE filename=%(image_filename)s AND experiment_id=(
                    SELECT _id FROM experiments as e WHERE e.name=%(image_experiment_name)s
                    )),
                (SELECT _id FROM labels
                    WHERE name=%(label_name)s AND experiment_id=(
                    SELECT _id FROM experiments as f WHERE f.name=%(label_experiment_name)s
                    )),
                (%(label_order)s) );
            """,
            {
                'image_filename': filename,
                'image_experiment_name': image_experiment_name,
                'label_name': label_name,
                'label_experiment_name': label_experiment_name,
                'label_order': label_order,
            }
            )
        if status_message:
            self.return_status('INSERT')


def initialize_database():
    config = dict(credentials.postgresql_connection(), **vars(db_config()))
    with db(config) as db_conn:
        db_conn.init_db()
        db_conn.return_status('CREATE')


def main():
    initialize_database()


if __name__ == '__main__':
    main()
