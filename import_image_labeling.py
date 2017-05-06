#!/usr/bin/env python
from settings.db_config import config as db_config
from ops import db, utilities, image_parser
from tqdm import tqdm
from argparse import ArgumentParser
from settings import credentials
import os


def main(
        experiment_name,
        parent_experiment=None,
        force_channels=True
        ):
    dbc = db_config()
    config = dict(credentials.postgresql_connection(), **vars(dbc))
    if dbc.experiment_name is None:
        raise RuntimeError(
            'Ya need to provide an experiment name in the config!')
    with db.db(config) as db_conn:
        exp_id = db_conn.add_experiment(  # add a new experiment
            experiment_name=dbc.experiment_name,
            parent_experiment=parent_experiment
            )
        for f in dbc.image_paths:
            files = utilities.get_files(f, dbc.image_file_filter)
            for fid in tqdm(
                    files,
                    desc='Inserting experiment %s' % dbc.experiment_name):
                w, h = image_parser.get_image_size(fid)
                if dbc.relative_path_pointer is not None:
                    fid = os.path.relpath(fid, start=dbc.relative_path_pointer)
                label, synset_parent, class_index = image_parser.get_image_label(
                    fid, dbc.image_key)
                if dbc.force_channels:
                    ch = 1  # need to figure out how to extract channels in image_parser
                if not dbc.child_dataset:
                    parent_label_id = None
                image_experiment_name = db_conn.add_images(
                    filename=fid,
                    encoding=dbc.encoding,
                    height=h,
                    width=w,
                    experiment_id=exp_id,
                    parent_image_id=synset_parent,
                    channels=ch)
                label_experiment_name = db_conn.add_labels(
                    name=label,
                    experiment_id=exp_id,
                    class_index=class_index,
                    parent_label_id=parent_label_id)
                if dbc.force_label_order:
                    label_order = None
                db_conn.add_image_label_join(
                    filename=fid,
                    image_experiment_name=image_experiment_name,
                    label_experiment_name=label_experiment_name,
                    label_order=label_order)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "--experiment_name", type=str, dest="experiment_name",
        default=None, help="Experiment name.")
    parser.add_argument(
        "--parent_experiment", type=str, dest="parent_experiment",
        default=None, help="Parent experiment name.")
    args = parser.parse_args()
    main(**vars(args))
