import sys
import os.path as op
from soma_workflow.client import Helper, Job, Workflow, Group


def generate_wf(wf_name, command_name, template_result,
                template_x, start_x, stop_x,
                template_y, start_y, stop_y,
                z_file,
                n_samples, n_perm, sparsity_threshold, seed):
    """
    """
    tasks = []
    for x_id in range(start_x, stop_x + 1):
        for y_id in range(start_y, stop_y + 1):
            cmd_name = command_name.rsplit('/')[-1]
            this_task = Job(
                command=["python", command_name,
                         str(n_samples), str(seed), str(n_perm),
                         z_file, template_y % y_id, template_x % x_id,
                         template_result % str("%d_%d" % (x_id, y_id)),
                         str(sparsity_threshold)],
                name=("%s %s" %
                      (cmd_name, str("x:%d y:%d" % (x_id, y_id)))))
            tasks.append(this_task)

    # create the workflow
    workflow = Workflow(jobs=tasks)

    # store the Workflow in a file
    Helper.serialize(wf_name, workflow)


if __name__ == '__main__':
    wf_dir = sys.argv[1]

    template_x = op.join(wf_dir, "snp_chunk_%d.npz")
    start_x = int(sys.argv[2])
    stop_x = int(sys.argv[3])  # inclusive

    template_y = op.join(wf_dir, "vox_chunk_%d.npz")
    start_y = int(sys.argv[4])
    stop_y = int(sys.argv[5])  # inclusive

    wf_name = op.join(wf_dir, ("mu_corr_cuda_%d_%d_%d_%d.json" %
               (start_x, stop_x, start_y, stop_y)))
    n_samples = int(sys.argv[6])
    z_file = op.join(wf_dir, "cov.npy")

    template_result = op.join(wf_dir, "result_%s.joblib")

    command_name = sys.argv[7]

    try:
        n_perm = int(sys.argv[8])
    except:
        n_perm = 10000
    try:
        sparsity_threshold = float(sys.argv[9])
    except:
        sparsity_threshold = 1e-4
    try:
        seed = int(sys.argv[10])
    except:
        seed = 0
    try:
        wf_subdir = sys.argv[11]
        template_result = op.join(wf_dir, wf_subdir)
        template_result = op.join(template_result, "result_%s.joblib")
    except:
        pass

    generate_wf(wf_name, command_name, template_result,
                template_x, start_x, stop_x,
                template_y, start_y, stop_y,
                z_file,
                n_samples, n_perm, sparsity_threshold, seed)
