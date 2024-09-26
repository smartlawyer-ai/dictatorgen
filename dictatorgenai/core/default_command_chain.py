from typing import Generator, List, Tuple
from .command_chain import CommandChain
from .general import General, TaskExecutionError

class DefaultCommandChain(CommandChain):
    def _select_dictator_and_generals(self, generals: List[General], task: str) -> Tuple[General, List[General]]:
        selected_generals = []
        dictator = None
        for general in generals:
            capability_level = general.can_execute_task(task)
            if capability_level.get("result") == "entirely":
                dictator = general
                selected_generals.append(general)
                break  # On a trouvé un dictateur capable, on peut sortir de la boucle
            elif capability_level.get("result") == "partially":
                selected_generals.append(general)
        if not dictator:
            if selected_generals:
                # Utiliser le premier général qui fait partie des selected_generals comme dictateur
                dictator = selected_generals[0]
            else:
                # Aucun général ne peut exécuter la tâche, lever une erreur
                raise TaskExecutionError("Aucun général n'est capable d'exécuter la tâche.")
        return dictator, selected_generals


    def solve_task(
        self,
        dictator: General,
        generals: List[General],
        task: str
    ) -> Generator[str, None, None]:
        if len(generals) == 1 and generals[0] == dictator:
            # Le dictateur résout la tâche seul
            yield f"{dictator.my_name_is} résout la tâche seul.\n"
            yield from dictator.solve_task(task)
        else:
            # Processus de résolution collective de la tâche
            combined_capabilities = [
                cap for general in generals for cap in general.my_capabilities_are
            ]
            assisting_generals = [g for g in generals if g != dictator]
            yield f"{dictator.my_name_is} résout la tâche avec l'aide de {', '.join([g.my_name_is for g in assisting_generals])}.\n"
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are an assistant with these collective capabilities: "
                        f"{', '.join(combined_capabilities)}. "
                        f"You solve the given task."
                    ),
                },
                {"role": "user", "content": f"The task to resolve is '{task}'"},
            ]
            # Appel au modèle d'IA via le dictateur
            yield from dictator.nlp_model.stream_chat_completion(messages)
