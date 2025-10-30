import os
from base_class import BaseClass
import random
import string
from collections import namedtuple
import yaml

Command = namedtuple(
    "Command",
    [
        "test",
        "test_list",
        "design_info",
        "sim",
        "tag",
        "max_error",
        "corner",
        "seed",
        "no_wave",
        "clk",
        "macro",
        "sim_path",
        "verbosity",
        "compile",
        "check_commits",
        "run_location",
        "CI",
    ],
)


class GenRunCommand(BaseClass):
    def __init__(self, paths) -> None:
        super().__init__()
        self.paths = paths
        self.cocotb_path = f"{self.paths.user_project_root}/verilog/dv/cocotb"
        self.update_design_info()
        self.rand_command = GenerateCommands(self.cocotb_path)

    def run_command(self, command):
        str = command[1]
        command_tuple = command[0]
        self.logger.info(f"[run_command] command string: {str}")
        self.logger.info(f"[run_command] command tuple: {command_tuple}")
        os.system(str)
        self.logger.info(f"[run_command] finished running command: {str}")

    def next_command(self):
        return self.rand_command.next_command()

    def is_all_cases_covered(self):
        # if all sim cases has been tested all other cases will be tested
        # since sims are the biggest essential list until sdf sims added to the CI
        return self.rand_command.sims_chooser.is_all_chosen

    def print_directory_tree(self, root_dir, indent=""):
        if not os.path.isdir(root_dir):
            self.logger.info("Invalid directory path.")
            return

        items = sorted(os.listdir(root_dir))

        for item in items:
            item_path = os.path.join(root_dir, item)
            if os.path.isdir(item_path):
                self.logger.info(f"{indent}+ {item}/")
                # self.print_directory_tree(item_path, indent + '  ')
            else:
                self.logger.info(f"{indent}- {item}")

    def update_design_info(self):
        data = {
            "CARAVEL_ROOT": self.paths.caravel_root,
            "MCW_ROOT": self.paths.mgmt_core_root,
            "USER_PROJECT_ROOT": self.paths.user_project_root,
            "PDK_ROOT": self.paths.pdk_root,
            "PDK": "sky130A",
            "clk": 25,
            "caravan": False,
            "emailto": [None],
        }

        with open(
            f"{self.paths.user_project_root}/verilog/dv/cocotb/design_info.yaml", "w"
        ) as file:
            yaml.dump(data, file)


class GenerateCommands(BaseClass):
    def __init__(self, cocotb_path) -> None:
        super().__init__()
        self.cocotb_path = cocotb_path
        self.all_switches_chooser()

    def all_switches_chooser(self):
        self.tests_chooser = RandomChooser(
            [None, "test_io10", "test_mgmt_gpio", "test_io10 test_mgmt_gpio"]
        )
        self.test_list_chooser = RandomChooser(
            [
                f"{self.cocotb_path}/test_io10/test_io10.yaml",
                f"{self.cocotb_path}/test_mgmt_gpio/test_mgmt_gpio.yaml",
            ]
        )
        self.design_infos_chooser = RandomChooser(
            [None, f"{self.cocotb_path}/design_info.yaml"]
        )
        self.sims_chooser = RandomChooser(
            [None, "RTL", "GL", "GL_SDF", "RTL GL", "GL RTL"]
        )
        self.tags_chooser = RandomChooser(
            [
                "".join(random.choice(string.ascii_lowercase) for _ in range(i))
                for i in range(5, 40)
            ]
        )  # change string length to make sure tag is unique
        self.max_errors_chooser = RandomChooser([None, "7", "5", "100"])
        self.corners_chooser = RandomChooser(
            [
                None,
                "nom-t",
                "nom-f",
                "nom-s",
                "max-t",
                "max-f",
                "max-s",
                "min-t",
                "min-f",
                "min-s",
            ]
        )
        self.seed_chooser = RandomChooser(
            [None] + [random.randint(0, 100000) for _ in range(5)]
        )
        self.no_wave_chooser = RandomChooser([None, None, True])
        self.clks_chooser = RandomChooser([None, 30, 40, 50])
        self.macros_chooser = RandomChooser([None, "USE_MACRO_1", "USE_MACRO_2"])
        self.sim_paths_chooser = RandomChooser(
            [None, os.path.abspath(os.path.join(self.cocotb_path, ".."))]
        )
        # self.verbosities_chooser = RandomChooser([None, "quiet", "normal", "debug"])
        self.verbosities_chooser = RandomChooser(["debug"])  # to speed sims
        self.compiles_chooser = RandomChooser([None, True])
        self.check_commits_chooser = RandomChooser([None, True])
        self.run_location = RandomChooser(
            [
                self.cocotb_path,
                os.path.abspath(os.path.join(self.cocotb_path, "..", "..")),
            ]
        )

    def next_command(self):
        ################### constrains ############################
        test = self.tests_chooser.choose_next()
        # force test_list to be None if test is provided and sim to be None if testlist is provided
        if test is not None:
            test_list = None
            sim = self.sims_chooser.choose_next()
        else:
            test_list = self.test_list_chooser.choose_next()
            sim = None
        design_info = self.design_infos_chooser.choose_next()
        # force run location to be in cocotb directory if design_info path file isn't provided
        if design_info is None:
            run_location = self.cocotb_path
        else:
            run_location = self.run_location.choose_next()
        #########################################################

        command = Command(
            test=test,
            test_list=test_list,
            design_info=design_info,
            sim=sim,
            tag=self.tags_chooser.choose_next(),
            max_error=self.max_errors_chooser.choose_next(),
            corner=self.corners_chooser.choose_next(),
            seed=self.seed_chooser.choose_next(),
            no_wave=self.no_wave_chooser.choose_next(),
            clk=self.clks_chooser.choose_next(),
            macro=self.macros_chooser.choose_next(),
            sim_path=self.sim_paths_chooser.choose_next(),
            verbosity=self.verbosities_chooser.choose_next(),
            compile=self.compiles_chooser.choose_next(),
            check_commits=self.check_commits_chooser.choose_next(),
            run_location=run_location,
            CI=True,
        )
        # force run location to be in cocotb directory if design_info path file isn't provided
        if command.design_info is None:
            command._replace(run_location=f"{self.cocotb_path}")
        # force test_list to be None if test is provided
        if command.test is not None:
            command._replace(test_list=None)
        command_str = self.generate_command_str(command)
        return (command, command_str)

    def generate_command_str(self, command):
        test = (
            f" -t {command.test} "
            if command.test is not None
            else f" -tl {command.test_list} "
        )
        design_info = (
            f" -design_info {command.design_info} "
            if command.design_info is not None
            else ""
        )
        sim = f" -sim {command.sim} " if command.sim is not None else ""
        max_error = (
            f" -maxerr {command.max_error} " if command.max_error is not None else ""
        )
        corner = f" -corner {command.corner} " if command.corner is not None else ""
        seed = f" -seed {command.seed} " if command.seed is not None else ""
        no_wave = " -no_wave " if command.no_wave is not None else ""
        clk = f" -clk {command.clk} " if command.clk is not None else ""
        macro = f" -macro {command.macro} " if command.macro is not None else ""
        sim_path = (
            f" -sim_path {command.sim_path} " if command.sim_path is not None else ""
        )
        verbosity = (
            f" -verbosity {command.verbosity} " if command.verbosity is not None else ""
        )
        compile = " -compile" if command.compile is not None else ""
        CI = " --CI" if command.CI is not None else ""
        # check_commits = " -check_commits" if command.check_commits is not None else ""
        # TODO for now remove using {check_commits}
        command = f"cd {command.run_location}  && caravel_cocotb {test}{design_info}{sim}{max_error}{corner}{seed}{no_wave}{clk}{macro}{sim_path}{verbosity}{compile}{CI} -tag  {command.tag}"
        return command


class RandomChooser:
    def __init__(self, items):
        self.items = items.copy()
        self.reset()
        self.is_all_chosen = False

    def reset(self):
        self.shuffled_items = self.items.copy()
        random.shuffle(self.shuffled_items)
        self.index = 0

    def choose_next(self):
        if self.index >= len(self.shuffled_items):
            self.is_all_chosen = True
            self.reset()
        chosen_item = self.shuffled_items[self.index]
        self.index += 1
        return chosen_item
