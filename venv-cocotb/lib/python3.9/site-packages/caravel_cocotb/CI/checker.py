from base_class import BaseClass
import yaml
import os
import xml.etree.ElementTree as ET


class Checker(BaseClass):
    def __init__(self):
        super().__init__()
        pass

    def check_command(self, command):
        self.command = command
        self.logger.info(f"[Checker] Check test {self.command}")
        all_tests_paths = self.get_expected_tests_dir()
        is_pass = self.check_exist_pass(all_tests_paths)
        if not is_pass:
            # don't do other checks in sdf sim because it didn't run
            return
        self.check_configs()
        self.check_seed(all_tests_paths)
        self.check_dump_wave(all_tests_paths)
        self.check_compile(all_tests_paths)
        self.check_macros(all_tests_paths)
        return

    def get_expected_tests_dir(self):
        self.logger.debug(
            f"[get_expected_tests_dir] Checking tests exist and pass test = {self.command.test} testlist = {self.command.test_list} sim = {self.command.sim}"
        )
        if self.command.sim is None:
            self.logger.debug("Sim is None")
            sims = ["RTL"]
        else:
            sims = self.command.sim.split()
        expected_tests = list()
        # to get tests run by -t
        if self.command.test is None:
            self.logger.debug("Test is None")
            tests = None
        else:
            tests = self.command.test.split()
            for sim_type in sims:
                for test_name in tests:
                    if sim_type != "GL_SDF":
                        expected_tests.append(f"{sim_type}-{test_name}")
                    else:
                        expected_tests.append(
                            f"{sim_type}-{test_name}-{'nom-t' if self.command.corner is None else self.command.corner}"
                        )
        # to get tests run by -tl
        if self.command.test_list is not None:
            with open(self.command.test_list, "r") as yaml_file:
                yaml_data = yaml_file.read()
            tests = yaml.safe_load(yaml_data).get("Tests", [])
            for test in tests:
                test_name = test.get("name")
                sim_type = test.get("sim")
                if sim_type != "GL_SDF":
                    expected_tests.append(f"{sim_type}-{test_name}")
                else:
                    expected_tests.append(
                        f"{sim_type}-{test_name}-{'nom-t' if self.command.corner is None else self.command.corner}"
                    )
        self.tag_path = f"{self.command.run_location if self.command.sim_path is None else self.command.sim_path}/sim/{self.command.tag}/"
        full_tests_paths = [
            self.tag_path + expected_test for expected_test in expected_tests
        ]
        self.logger.info(f"[get_expected_tests_dir] Expected tests: {full_tests_paths}")
        return full_tests_paths

    def check_exist_pass(self, all_tests_paths):
        for test_path in all_tests_paths:
            if os.path.exists(test_path):
                self.logger.info(f"[check_exist_pass] Test {test_path} exists")
            else:
                raise ValueError(f"[check_exist_pass] Test {test_path} doesn't exist")
                return False

            if os.path.exists(f"{test_path}/passed"):
                self.logger.info(f"[check_exist_pass] Test {test_path} passed")
            else:
                if self.command.sim != "GL_SDF":
                    raise ValueError(f"[check_exist_pass] Test {test_path} failed")
                return False
        return True

    def check_configs(self):
        # read design_info.yaml
        design_info_path = (
            self.command.design_info
            if self.command.design_info is not None
            else f"{self.command.run_location}/design_info.yaml"
        )
        with open(design_info_path, "r") as yaml_file:
            yaml_data = yaml_file.read()
        design_info = yaml.safe_load(yaml_data)
        caravel_root_exp = design_info.get("CARAVEL_ROOT")
        mgmt_core_exp = design_info.get("MCW_ROOT")
        pdk_root_exp = design_info.get("PDK_ROOT") + "/" + design_info.get("PDK")
        pdk_exp = design_info.get("PDK")[:-1]
        clk_exp = (
            self.command.clk if self.command.clk is not None else design_info.get("clk")
        )
        max_err_exp = (
            int(self.command.max_error) if self.command.max_error is not None else 3
        )

        # read configs.yaml generated
        config_path = f"{self.tag_path}/configs.yaml"
        with open(config_path, "r") as yaml_file:
            yaml_data = yaml_file.read()
        configs = yaml.safe_load(yaml_data)
        if clk_exp != configs.get("clock"):
            raise ValueError(
                f"[check_configs] Clock mismatch: {clk_exp} != {configs.get('clock')}"
            )
        if max_err_exp != int(configs.get("max_err")):
            raise ValueError(
                f"[check_configs] Max error mismatch: {max_err_exp} != {configs.get('max_err')}"
            )
        if caravel_root_exp != configs.get("CARAVEL_ROOT"):
            raise ValueError(
                f"[check_configs] Caravel root mismatch: {caravel_root_exp} != {configs.get('CARAVEL_ROOT')}"
            )
        if mgmt_core_exp != configs.get("MCW_ROOT"):
            raise ValueError(
                f"[check_configs] Management core mismatch: {mgmt_core_exp} != {configs.get('MCW_ROOT')}"
            )
        if pdk_root_exp != configs.get("PDK_ROOT"):
            raise ValueError(
                f"[check_configs] PDK root mismatch: {pdk_root_exp} != {configs.get('PDK_ROOT')}"
            )
        if pdk_exp != configs.get("PDK"):
            raise ValueError(
                f"[check_configs] PDK mismatch: {pdk_exp} != {configs.get('PDK')}"
            )

    def check_seed(self, all_tests_paths):
        if self.command.seed is not None:
            for test_path in all_tests_paths:
                seed_file_path = f"{test_path}/seed.xml"
                with open(seed_file_path, "r") as xml_file:
                    xml_content = xml_file.read()

                # Parse the XML content
                root = ET.fromstring(xml_content)

                # Find the random_seed property and extract its value
                seed_value = None
                for testsuite in root.findall(".//testsuite"):
                    seed_elem = testsuite.find(".//property[@name='random_seed']")
                    if seed_elem is not None:
                        seed_value = int(seed_elem.get("value"))
                        break
                if seed_value == self.command.seed:
                    self.logger.info(
                        f"[check_seed] Test run with correct seed {seed_value}"
                    )
                else:
                    raise ValueError(
                        f"[check_seed] Test run with incorrect seed {seed_value} instead of {self.command.seed}"
                    )

    def check_dump_wave(self, all_tests_paths):
        dump_wave_exp = False if self.command.no_wave is not None else True
        for test_path in all_tests_paths:
            if os.path.exists(f"{test_path}/waves.vcd") and not dump_wave_exp:
                raise ValueError(
                    f"[check_dump_wave] Test {test_path} dump waves while -no_wave switch is used"
                )
            elif not os.path.exists(f"{test_path}/waves.vcd") and dump_wave_exp:
                raise ValueError(
                    f"[check_dump_wave] Test {test_path} doesn't dump waves while -no_wave switch isn't used"
                )
            else:
                self.logger.info(
                    f"[check_dump_wave] Test {test_path} has wave {'dumped' if dump_wave_exp else 'not dumped'} waves as expected"
                )

    def check_compile(self, all_tests_paths):
        is_compile_shared = True if self.command.compile is None else False
        for test_path in all_tests_paths:
            simvpp_exist = os.path.exists(f"{test_path}/sim.vvp")
            if simvpp_exist and is_compile_shared:
                raise ValueError(
                    f"[check_compile] Test {test_path} compile is not shared while -compile switch is used"
                )
            elif not simvpp_exist and not is_compile_shared:
                raise ValueError(
                    f"[check_compile] Test {test_path} shared compile while -compile switch isn't used simvpp exist = {simvpp_exist} is shared = {is_compile_shared}"
                )
            else:
                self.logger.info(
                    f"[check_compile] Test {test_path} has compile {'shared' if is_compile_shared else 'not shared'} as expected"
                )

    def check_macros(self, all_tests_paths):
        macro_used = self.command.macro
        if macro_used is not None:
            pattern_to_search = f"Found {macro_used} effect"
            for test_path in all_tests_paths:
                # search pattern in all .log files
                for filename in os.listdir(test_path):
                    if filename.endswith(".log"):
                        file_log = os.path.join(test_path, filename)
                        with open(file_log, "r") as log_file:
                            content = log_file.read()
                            if pattern_to_search in content:
                                self.logger.info(
                                    f"[check_macros] Test {test_path} uses macro {macro_used} correctly"
                                )
                                return True
                raise ValueError(
                    f"[check_macros] Test {test_path} doesn't use macro {macro_used}"
                )
                return False
