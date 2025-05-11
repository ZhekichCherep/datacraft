from .pipeline_saver import PipelineSaver
from .num_preprocessing import NUM_COLS_STRATEGY
from core.modules.fstream_operations import read_work_file, save_work_file

def apply_pipeline(path_to_pipeline: str, path_to_file: str, path_to_config: str) -> None:
    pipeline_saver = PipelineSaver(False, path_to_pipeline)
    steps = pipeline_saver.get_steps()
    df = read_work_file(path_to_file, path_to_config)

    for column in list(steps.keys()):
        for process in list(steps[column].keys()):
            df = NUM_COLS_STRATEGY[process](df, [column], pipeline_saver)

    save_work_file(df, path_to_file, path_to_config)
    