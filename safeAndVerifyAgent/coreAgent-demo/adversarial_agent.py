import os
import json
import subprocess
import threading
from typing import Optional, List, Dict, Any


class AdversarialAgent:
    """Wrapper around the multiModalAdversarialAttackFramework to prepare and launch attacks.

    This class writes the AE_thread_info.json expected by the project's `subprocess0319.py`
    and then runs that script in the framework `src` folder. It provides convenience methods
    for the 5 task types used by `common.attacks`:
      0 - image classification
      1 - object detection
      2 - semantic segmentation
      3 - audio
      4 - text

    Notes:
    - The wrapper uses the framework's relative paths, so `framework_src` should point to
      the `multiModalAdversarialAttackFramework/src` directory.
    - Attack execution is generally long-running. Use `run_in_background=True` to start
      the subprocess in a background thread and get a handle to the Thread object.
    """

    def __init__(self, framework_src: str):
        self.framework_src = os.path.abspath(framework_src)
        if not os.path.isdir(self.framework_src):
            raise ValueError(f"framework_src not found: {self.framework_src}")

    def _write_thread_info(self, info: Dict[str, Any]):
        path = os.path.join(self.framework_src, 'AE_thread_info.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(info, f)
        return path

    def _run_subprocess_script(self, run_in_background: bool = False):
        script = os.path.join(self.framework_src, 'subprocess0319.py')

        def target():
            # Run the attack subprocess and stream output to caller's stdout
            proc = subprocess.Popen(["python", script], cwd=self.framework_src,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
            # Print lines as they come
            if proc.stdout is not None:
                for line in iter(proc.stdout.readline, b""):
                    try:
                        print(line.decode().rstrip())
                    except Exception:
                        pass
            proc.wait()
            return proc.returncode

        if run_in_background:
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            return thread
        else:
            return target()

    def prepare_and_run_attack(self,
                               task: int,
                               model_name: str,
                               dataset_name: str,
                               method_name: str,
                               epsilons: List[float],
                               save_path: str = '../adv-img/',
                               save_boxes_path: Optional[str] = None,
                               substitute: bool = True,
                               targeted: bool = False,
                               distance_str: Optional[str] = None,
                               run_in_background: bool = False) -> Any:
        """Prepare AE_thread_info.json and launch the attack runner.

        Returns either the thread (if run_in_background=True) or the subprocess return code.
        """
        info = {
            "model_name": model_name,
            "dataset_name": dataset_name,
            "task": task,
            "save_path": save_path,
            "save_boxes_path": save_boxes_path,
            "substitute": substitute,
            "method_name": method_name,
            "targeted": targeted,
            "distance_str": distance_str,
            "epsilons": epsilons,
        }
        self._write_thread_info(info)
        return self._run_subprocess_script(run_in_background=run_in_background)

    # Convenience wrappers for modality-specific attacks
    def attack_image_classification(self, model_name: str, dataset_name: str, method_name: str,
                                    epsilons: List[float], **kwargs):
        return self.prepare_and_run_attack(task=0, model_name=model_name, dataset_name=dataset_name,
                                           method_name=method_name, epsilons=epsilons, **kwargs)

    def attack_object_detection(self, model_name: str, dataset_name: str, method_name: str,
                                epsilons: List[float], save_boxes_path: Optional[str] = '../results-img/object-detection/', **kwargs):
        return self.prepare_and_run_attack(task=1, model_name=model_name, dataset_name=dataset_name,
                                           method_name=method_name, epsilons=epsilons,
                                           save_boxes_path=save_boxes_path, **kwargs)

    def attack_segmentation(self, model_name: str, dataset_name: str, method_name: str,
                             epsilons: List[float], save_boxes_path: Optional[str] = '../results-img/semantic-segmentation/', **kwargs):
        return self.prepare_and_run_attack(task=2, model_name=model_name, dataset_name=dataset_name,
                                           method_name=method_name, epsilons=epsilons,
                                           save_boxes_path=save_boxes_path, **kwargs)

    def attack_audio(self, model_name: str, dataset_name: str, method_name: str, epsilons: List[float], **kwargs):
        # In the framework audio attack expects an epsilon scalar; we keep epsilons list for consistency
        return self.prepare_and_run_attack(task=3, model_name=model_name, dataset_name=dataset_name,
                                           method_name=method_name, epsilons=epsilons, **kwargs)

    def attack_text(self, model_name: str, dataset_name: str, method_name: str = '', epsilons: List[float] = [], **kwargs):
        return self.prepare_and_run_attack(task=4, model_name=model_name, dataset_name=dataset_name,
                                           method_name=method_name, epsilons=epsilons, **kwargs)


if __name__ == '__main__':
    print('adversarial_agent module loaded. Use AdversarialAgent(framework_src) to control attacks.')
