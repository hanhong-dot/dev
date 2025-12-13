import os
import Deadline.DeadlineConnect as Connect


def submit_job(task_name, py_path, argument_str):
    host_name = "10.10.201.175"
    con = Connect.DeadlineCon(host_name, 8082)
    JobInfo = dict(
        Name=task_name,
        Frames="1",
        Plugin="Python",
        OnJobComplete="Delete",
        # m_test  cloth_solve
        Pool="cloth_solve",
        Priority=91,
        TaskTimeoutMinutes=90,
        OnTaskTimeout="ErrorAndNotify",
        OverrideTaskFailureDetection=True,
        OverrideJobFailureDetection=True,
        FailureDetectionJobErrors=1,
        FailureDetectionTaskErrors=1,

    )
    PluginInfo = dict(
        ScriptFile=py_path,
        Arguments=argument_str,
        Version=2.7,
    )
    new_job = con.Jobs.SubmitJob(JobInfo, PluginInfo)
    # new_job["Props"]["MaxTime"] = 60 * 20
    # new_job["Props"]["Timeout"] = 7
    # new_job["Props"]["OnComp"] = 1
    # con.Jobs.SaveJob(new_job)


def submit_task(py_path, path):
    py_path = py_path.replace("\\", "/")
    path = path.replace("\\", "/")
    base_name = os.path.splitext(os.path.basename(path))[0]
    task_name = base_name
    argument = "-path {path}".format(**locals())
    submit_job(task_name, py_path, argument)


def submit_random_all(anim_dir):
    anim_dir = anim_dir.replace("\\", "/")
    py_path = r"L:/scripts/aiMetaTool2/metaNN/meta_nn_task.py"
    for i in range(4, 4000, 1):
        n = "meta_nn_%05i_task" % i
        path = os.path.join(anim_dir, n).replace("\\", "/")
        submit_task(py_path, path)


def test():
    submit_random_all(r"K:/mh_face_random/v3")


if __name__ == '__main__':
    test()
