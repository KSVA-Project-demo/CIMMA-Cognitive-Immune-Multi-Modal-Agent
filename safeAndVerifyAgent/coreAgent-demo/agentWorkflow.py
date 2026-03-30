"""Basic agent workflow for using multi-modal adversarial attacks from the project.

This file provides a robot-level adversarial agent that composes the lower-level
`AdversarialAgent` (see `adversarial_agent.py`) and exposes simple methods the
robot can call when it wants to perturb one or more modalities (image, text, audio)
during tasks such as object recognition / sorting and path planning / obstacle avoidance.

The implementation purposefully keeps execution separate from heavy compute by
delegating to the framework's `subprocess0319.py` via the wrapper in
`adversarial_agent.AdversarialAgent`.
"""

from typing import Dict, Any, Optional
import os

from adversarial_agent import AdversarialAgent


class RobotAdversarialAgent:
	"""High-level agent that orchestrates modality attacks for robot tasks.

	Usage example:
		framework_src = r"d:/projectspycharm/CIMMA-demo/safeAndVerifyAgent/multiModalAdversarialAttackFramework/src"
		agent = RobotAdversarialAgent(framework_src)
		# Launch an image classification attack (runs framework subprocess)
		agent.attack_image(model_name='ResNet50', dataset_name='CIFAR10', method='L2ProjectedGradientDescentAttack', epsilons=[0.03], run_in_background=True)
	"""

	def __init__(self, framework_src: str):
		self.framework_src = os.path.abspath(framework_src)
		self._aa = AdversarialAgent(self.framework_src)

	def attack_image(self, model_name: str, dataset_name: str, method: str, epsilons: list,
					 run_in_background: bool = True, **kwargs) -> Optional[Any]:
		"""Attack image classification models. Returns thread or return code."""
		return self._aa.attack_image_classification(model_name=model_name, dataset_name=dataset_name,
													method_name=method, epsilons=epsilons,
													run_in_background=run_in_background, **kwargs)

	def attack_detection(self, model_name: str, dataset_name: str, method: str, epsilons: list,
						 run_in_background: bool = True, **kwargs) -> Optional[Any]:
		return self._aa.attack_object_detection(model_name=model_name, dataset_name=dataset_name,
												method_name=method, epsilons=epsilons,
												run_in_background=run_in_background, **kwargs)

	def attack_segmentation(self, model_name: str, dataset_name: str, method: str, epsilons: list,
							 run_in_background: bool = True, **kwargs) -> Optional[Any]:
		return self._aa.attack_segmentation(model_name=model_name, dataset_name=dataset_name,
											method_name=method, epsilons=epsilons,
											run_in_background=run_in_background, **kwargs)

	def attack_audio(self, model_name: str, dataset_name: str, method: str, epsilons: list,
					 run_in_background: bool = True, **kwargs) -> Optional[Any]:
		return self._aa.attack_audio(model_name=model_name, dataset_name=dataset_name,
									 method_name=method, epsilons=epsilons,
									 run_in_background=run_in_background, **kwargs)

	def attack_text(self, model_name: str, dataset_name: str, method: str = '', epsilons: list = [],
					run_in_background: bool = True, **kwargs) -> Optional[Any]:
		return self._aa.attack_text(model_name=model_name, dataset_name=dataset_name,
									method_name=method, epsilons=epsilons,
									run_in_background=run_in_background, **kwargs)

	def orchestrate_for_robot(self, perception: Dict[str, Any], task: str, policy: Dict[str, Any] = None):
		"""Example high-level orchestrator.

		perception: dict containing 'image' (path), 'text' (string), 'audio' (path) where available.
		task: 'sorting' or 'navigation' (used to select which modalities to attack)
		policy: optional dict to control which attack parameters to use.

		This method does NOT run heavy attacks itself; it delegates to the framework and returns
		immediately if run_in_background=True.
		"""
		if policy is None:
			policy = {}

		results = {}
		if task == 'sorting':
			# Sorting primarily depends on image classification + text label mapping
			if 'image' in perception:
				results['image_thread'] = self.attack_image(
					model_name=policy.get('image_model', 'ResNet50'),
					dataset_name=policy.get('image_dataset', 'CIFAR10'),
					method=policy.get('image_method', 'L2ProjectedGradientDescentAttack'),
					epsilons=policy.get('image_eps', [0.03]),
					run_in_background=policy.get('background', True)
				)
			if 'text' in perception:
				results['text_thread'] = self.attack_text(
					model_name=policy.get('text_model', 'wordLSTM'),
					dataset_name=policy.get('text_dataset', 'ag'),
					method=policy.get('text_method', ''),
					epsilons=policy.get('text_eps', []),
					run_in_background=policy.get('background', True)
				)

		elif task == 'navigation':
			# Navigation often relies on segmentation/obstacle detection and sometimes audio (commands)
			if 'image' in perception:
				results['seg_thread'] = self.attack_segmentation(
					model_name=policy.get('seg_model', 'transform'),
					dataset_name=policy.get('seg_dataset', 'robot'),
					method=policy.get('seg_method', 'SegPGD-BlockBox'),
					epsilons=policy.get('seg_eps', [0.5]),
					run_in_background=policy.get('background', True)
				)
			if 'audio' in perception:
				results['audio_thread'] = self.attack_audio(
					model_name=policy.get('audio_model', 'ResNet18'),
					dataset_name=policy.get('audio_dataset', 'AudioMNIST'),
					method=policy.get('audio_method', 'PGD'),
					epsilons=policy.get('audio_eps', [0.005]),
					run_in_background=policy.get('background', True)
				)

		else:
			raise ValueError('Unknown task: ' + task)

		return results


if __name__ == '__main__':
	# Example usage (dry run): do not launch heavy attacks by default
	framework_src = os.path.join('..', 'multiModalAdversarialAttackFramework', 'src')
	print('Creating RobotAdversarialAgent for framework at', framework_src)
	agent = RobotAdversarialAgent(framework_src)
	print('Agent ready. Use agent.orchestrate_for_robot(...) to schedule attacks.')

