import config

class DataHost:
    """Class for handling compute host data"""

    @staticmethod
    def get_vcpus_used(host):
        """
        Get vCPUs used by a compute host

        Args:
            host (str): Compute host name

        Returns:
            int: Number of vCPUs used
        """
        with open(config.ALLOCATION_FILE_PATH, 'r') as allocation_file:
            vcpus_used = 0
            for line in allocation_file:
                parts = line.strip().split()
                if len(parts) >= 6 and parts[1] == host:
                    vcpus_used = int(parts[5])
                    break
            return vcpus_used

    @staticmethod
    def get_vcpus_ratio(host):
        """
        Get vCPUs ratio for a compute host

        Args:
            host (str): Compute host name

        Returns:
            float: vCPUs ratio
        """
        with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
            vcpus_ratio = 0.0
            for line in ratio_file:
                parts = line.strip().split(', ')
                if len(parts) == 3 and parts[0] == host:
                    vcpus_ratio = float(parts[1])
            return vcpus_ratio

    @staticmethod
    def get_vcpus_total(host):
        """
        Get total vCPUs for a compute host

        Args:
            host (str): Compute host name

        Returns:
            float: Total vCPUs
        """
        return DataHost.get_vcpus_ratio(host) * config.CORE_COMPUTE

    @staticmethod
    def get_vcpus_free(host):
        """
        Get free vCPUs for a compute host

        Args:
            host (str): Compute host name

        Returns:
            float: Free vCPUs
        """
        return DataHost.get_vcpus_total(host) - DataHost.get_vcpus_used(host)

    @staticmethod
    def get_ram_used(host):
        """
        Get RAM used by a compute host in MB

        Args:
            host (str): Compute host name

        Returns:
            int: Amount of RAM used in MB
        """
        with open(config.ALLOCATION_FILE_PATH, 'r') as allocation_file:
            ram_used = 0
            for line in allocation_file:
                parts = line.strip().split()
                if len(parts) >= 8 and parts[1] == host:
                    ram_used = int(parts[7])
                    break
            return ram_used

    @staticmethod
    def get_ram_total(host):
        """
        Get total RAM for a compute host in MB

        Args:
            host (str): Compute host name

        Returns:
            int: Total amount of RAM in MB
        """
        with open(config.ALLOCATION_FILE_PATH, 'r') as allocation_file:
            ram_total = 0
            for line in allocation_file:
                parts = line.strip().split()
                if len(parts) >= 9 and parts[1] == host:
                    ram_total = int(parts[8])
                    break
            return ram_total

    @staticmethod
    def get_ram_free(host):
        """
        Get free RAM for a compute host in MB

        Args:
            host (str): Compute host name

        Returns:
            int: Amount of free RAM in MB
        """
        return DataHost.get_ram_total(host) - DataHost.get_ram_used(host)

    @staticmethod
    def get_ram_ratio(host):
        """
        Get RAM ratio for a compute host

        Args:
            host (str): Compute host name

        Returns:
            float: RAM ratio
        """
        with open(config.RATIO_FILE_PATH, 'r') as ratio_file:
            ram_ratio = 0.0
            for line in ratio_file:
                parts = line.strip().split(', ')
                if len(parts) == 3 and parts[0] == host:
                    ram_ratio = float(parts[2])
            return ram_ratio
