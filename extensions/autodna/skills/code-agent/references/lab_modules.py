# lab_modules.py
from scheduler import call_machine_command 
from abc import ABC, abstractmethod
from enum import IntEnum, Enum
from typing import List, Union, Optional, TypedDict
import abc
from enum import Enum



# --- Provided Context ---

class Location:
    # Usage: The location of a machine or container
    def __init__(self, description: str):
        self.description = description

DEFAULT_CONTAINERHOLDER_LOCATION = Location("ContainerHolder")
class BaseMachine:
    def __init__(self, location: Location):
        self.location = location

    def get_location(self) -> Location:
        return self.location

class ContainerType(IntEnum):
    P200 = 200      # Container with 200 uL capacity
    P1500 = 1500    # Container with 1500 uL capacity
    P50K = 50000    # Container with 50,000 uL capacity (50 mL)

class Container:
    """Model for lab containers (e.g., tubes, plates)."""
    def __init__(self, label: str, index: int, capacity: ContainerType = ContainerType.P200, volume: float = 0.0, replenishable: bool = False, location: Optional[Location] = None):
        self.index = index
        self.volume = volume
        self.capacity = max(capacity.value, volume)
        self.label = label # The identifier for the container
        self.capped = False  # Containers are uncapped by default
        self.replenishable = replenishable # Containers can be automatically refilled if True
        self.location = location
        
class ContainerManager:

    # Current index of the container to be allocated
    _nextContainerIndex = 1000
    _nextContainerLocation = DEFAULT_CONTAINERHOLDER_LOCATION

    def __init__(self):
        self.containerList = []

    # Method: getNewContainer
    # Usage: Allocate a new empty container for use
    # Params: 
    #   - cap: The capacity of the allocated container (uL). 
    #   - label: The label of the allocated container. (recommended to have different labels for different tubes)
    #   - location: The location of the allocated container.
    def newContainer(self, label: str, cap: ContainerType = ContainerType.P200) -> Container:
        index = ContainerManager._nextContainerIndex
        container = Container(label = label, index = index, capacity = cap, volume = 0, location = DEFAULT_CONTAINERHOLDER_LOCATION)
        self.containerList.append(container)
        ContainerManager._nextContainerIndex += 1
        call_machine_command("container_allocate", {
            "container_index": container.index,
            "container_label": container.label
        })
        return container

    # Method: getContainerForReplenish
    # Usage: Get a container from repo or get a used container 
    def getContainerForReplenish(self, name, required_volume = 0) -> Container:

        container = Container(label = name, index = ContainerManager._nextContainerIndex, capacity = ContainerType.P200 if required_volume <= 200 else ContainerType.P50K, volume = required_volume, location = ContainerManager._nextContainerLocation, replenishable = True)
        self.containerList.append(container)
        ContainerManager._nextContainerLocation = DEFAULT_CONTAINERHOLDER_LOCATION
        ContainerManager._nextContainerIndex += 1
        call_machine_command("container_get", {
            "container_index": container.index,
            "container_label": container.label
        })
        return container
    
class PortType(Enum):
    """Enumeration for the types of ports a robot can interact with."""
    PRIMING = "Priming-Port"
    SPOTON = "SpotON"

class Port:
    """Represents an accessible port on a piece of lab equipment."""
    def __init__(self, port_type: PortType):
        self.port_type = port_type
        
    def get_tube(self):
        container = container_manager.getContainerForReplenish(self.port_type.name)
        container.capacity = ContainerType.P50K
        return container

class Timer:
    """A non-physical machine for pausing execution."""
    def wait(self, time: int):
        call_machine_command("timer_wait", {
            "time": time
        })

DEFAULT_CAPPER_LOCATION = Location("capper")
class Capper_200ul_tubes(BaseMachine, abc.ABC):
    """
    An abstract base class for an automatic capper for 8-strip, 200µL PCR tubes.

    This interface models a device that performs a single "one-touch" operation:
    to securely and uniformly seal an 8-tube strip that has been manually
    placed into the device by a user.
    """
    def __init__(self, location: Location = DEFAULT_CAPPER_LOCATION):
        super().__init__(location)
        
    
    def cap(self) -> None:
        """
        Executes a single, complete capping cycle.

        This method assumes that a compatible 8-tube strip and its corresponding
        cap strip have already been correctly placed in the device's slot.
        The call should block until the capping cycle is complete.

        Raises:
            MachineBusyError: If a capping cycle is already in progress.
            CappingError: If the capping operation fails due to a machine
                          fault, incorrect consumable placement, or other issue.
        """
        call_machine_command("capper_cap_container", {
        })
        
DEFAULT_CENTRIFUGE_P1500_LOCATION = Location("centrifuge_P1500")
class Centrifuge1p5mL(BaseMachine, abc.ABC):
    """
    Abstract base class for a 'Centrifuge (1.5ml tubes)'.

    This class defines the standard interface for operating a microcentrifuge
    that is specifically designed for standard 1.5ml centrifuge tubes,
    as described in the Quick Start Guide.
    """
    def __init__(self, location: Location = DEFAULT_CENTRIFUGE_P1500_LOCATION):
        super().__init__(location)

    def run(self, speed_rpm: int, duration_seconds: int) -> None:
        """
        Sets the parameters and starts a centrifugation cycle.

        This method is blocking and will only return after the centrifugation
        run has completed. It combines the 'Set Speed', 'Set Duration', and
        'Start' steps from the user guide into a single, explicit command.

        Args:
            speed_rpm: The desired rotational speed in revolutions per minute (RPM).
            duration_seconds: The desired duration of the run in seconds.
        """
        call_machine_command("centrifuge_start", {
            "time": duration_seconds,
            "speed": speed_rpm,
            "container_type": ContainerType.P1500
        })

DEFAULT_CENTRIFUGE_P200_LOCATION = Location("centrifuge_P200")
class Centrifuge_200ulTubes(BaseMachine, abc.ABC):
    """
    An abstract base class for a microcentrifuge that operates on
    standard 200ul 8-strip tubes.

    This interface models the core functionality of setting speed and
    duration, and then running a centrifugation cycle.
    """

    def __init__(self, location: Location = DEFAULT_CENTRIFUGE_P200_LOCATION):
        super().__init__(location)

    def run(self, speed_rpm: int = 2500, duration_sec: int = 15) -> None:
        """
        Starts a centrifugation cycle with the specified parameters.

        This is a blocking operation; it will not return until the cycle
        is complete. The user is expected to have loaded the compatible
        8-strip tubes before calling this method.

        Based on the operating steps:
        1. Set Speed (speed_rpm)
        2. Set Duration (duration_sec)
        3. Start

        Args:
            speed_rpm: The rotational speed in revolutions per minute (RPM).
                       Defaults to a typical value for a "quick spin".
            duration_sec: The duration of the spin in seconds.
                          Defaults to a typical value for a "quick spin".
        """
        call_machine_command("centrifuge_start", {
            "time": duration_sec,
            "speed": speed_rpm,
            "container_type": ContainerType.P200
        })

DEFAULT_FLUOROMETER_LOCATION = Location("fluorometer")
# Can be used for qpcr fluorescence measurement
class Fluorometer200ul(BaseMachine, ABC):
    """
    An abstract base class representing a fluorometer designed for up to eight
    concurrent 200µL tubes.

    This interface defines the essential operations for fluorescence-based
    quantification and raw signal measurement, based on a two-point calibration
    system.
    """
    
    def __init__(self, location: Location = DEFAULT_FLUOROMETER_LOCATION):
        super().__init__(location)

    def calibrate(
        self,
        standard1_concentration: float,
        standard2_concentration: float,
        unit: str,
    ) -> None:
        """
        Performs a two-point calibration for concentration measurements.

        The implementation should handle the process of reading the two provided
        standards. The resulting calibration is stored internally for
        subsequent calls to `measure_concentration`.

        Args:
            standard1_concentration: The known concentration of the first standard.
            standard2_concentration: The known concentration of the second standard.
            unit: The unit of concentration (e.g., 'ng/µL'). This unit will be
                  used for the results of `measure_concentration`.

        Raises:
            Exception: If the calibration process fails for any reason (e.g.,
                       hardware error, invalid readings).
        """
        pass

    def measure_concentration(self, sample_volume_ul: int = 10) -> List[float]:
        """
        Measures the concentration of samples in all eight wells.

        A calibration must be successfully performed via the `calibrate` method
        before using this function.

        Args:
            sample_volume_ul: The volume of the initial sample added to the
                              assay tube, in microliters (µL). Defaults to 10.
                              Valid range is typically 1-20 µL.

        Returns:
            A list of eight floats, representing the calculated concentration
            for each corresponding well (1 through 8). The unit is determined
            by the `unit` provided during the last successful calibration.

        Raises:
            Exception: If the instrument has not been calibrated or if the
                       measurement fails.
        """
        value = call_machine_command("fluorometer_concentration", {
        })
        return value

    def measure_fluorescence(self) -> List[int]:
        """
        Measures the raw fluorescence signal from all eight wells.

        This method provides the raw Relative Fluorescence Units (RFU) and does
        not require prior calibration.

        Returns:
            A list of eight integers, representing the raw fluorescence
            signal (RFU) for each corresponding well (1 through 8).
        """
        value = call_machine_command("fluorometer_measure", {
        })
        return value
        
DEFAULT_HEATER_LOCATION = Location("heater")
class Heater1_5mlTubes(BaseMachine, ABC):
    """
    Abstract base class for a heating incubator designed for 1.5ml sample tubes.

    This interface defines the essential controls for setting temperature and
    running timed or indefinite incubation processes, based on the operating
    steps of the Model TH-1500.
    """
    def __init__(self, location: Location = DEFAULT_HEATER_LOCATION):
        super().__init__(location)

    def start(self, temperature_celsius: float, duration_minutes: Optional[float] = None) -> None:
        """
        Starts the heating process.

        This single method handles both indefinite heating and timed incubations,
        reflecting the core functionalities of "Set Temperature" and "Set Time".

        Args:
            temperature_celsius: The target temperature in degrees Celsius.
            duration_minutes: The incubation time in minutes. If None, the heater
                              will maintain the target temperature indefinitely.
        """
        call_machine_command("heater_start", {
            "time": duration_minutes * 60,
            "temperature": temperature_celsius
        })

    def stop(self) -> None:
        """
        Immediately stops any active heating or timed incubation process.
        The heater will begin to cool down passively.
        """
        pass

    def get_current_temperature(self) -> float:
        """
        Returns the current temperature of the heating block in degrees Celsius.

        Returns:
            The current temperature as a float.
        """
        return 0.0
    
DEFAULT_HEATERSHAKER_LOCATION = Location("heater_shaker")
class HeaterShaker200uL(BaseMachine, ABC):
    """
    An abstract base class for a heated shaker, typically used with 200ul tubes.

    This interface provides simple controls for setting temperature and shaking speed
    for a specified duration.
    """

    def __init__(self, location: Location = DEFAULT_HEATERSHAKER_LOCATION):
        super().__init__(location)
        
    def incubate(
        self,
        target_temperature_celsius: Optional[float] = None,
        target_speed_rpm: int = 1300,
        duration_seconds: Optional[int] = None
    ) -> None:
        """
        Starts a heating and/or shaking protocol.

        At least one of `target_temperature_celsius` or `target_speed_rpm` must
        be provided to start an incubation.

        Args:
            target_temperature_celsius: The target temperature in Celsius. If None,
                the heater remains off.
            target_speed_rpm: The target shaking speed in revolutions per minute.
                The minimum speed is typically around 110 RPM.
            duration_seconds: The duration of the incubation in seconds. If None, the
                incubation runs indefinitely until `stop()` is called.
        """
        call_machine_command("heatershaker_start", {
            "time": duration_seconds,
            "temperature": target_temperature_celsius,
            "speed": target_speed_rpm
        })

    def stop(self) -> None:
        """
        Safely stops all heating and shaking operations.

        This method will immediately turn off the heater and initiate a safe
        deceleration of the shaker.
        """
        pass

    def get_current_temperature_celsius(self) -> float:
        """
        Returns the current temperature of the heating block in Celsius.
        """
        return 0.0

    def get_current_speed_rpm(self) -> int:
        """
        Returns the current shaking speed in revolutions per minute.
        """
        return 0

DEFAULT_MAGRACKP1500_LOCATION = Location("magrack_P1500")
class MagRackP1500(BaseMachine, ABC):
    """
    An abstract base class for a passive magnetic rack for 1.5ml tubes.

    This rack uses permanent magnets to separate paramagnetic beads from a
    solution. Based on the principle of operation, the magnetic field is always
    active. The core operation involves placing a tube in the rack and waiting
    for a pellet to form.
    """

    def __init__(self, location: Location = DEFAULT_MAGRACKP1500_LOCATION, model: str = "MS-08"):
        """
        Initializes the MagRack.

        Args:
            location: The physical location of the magnetic rack.
            model: The specific model identifier of the rack, e.g., "MS-08".
        """
        super().__init__(location)
        self.model: str = model
        self.capacity: int = 8
        self.compatible_tube_type: str = "1.5ml PCR Tube"

    def separate(self, wait_duration_seconds: int = 60) -> None:
        """
        Performs the magnetic separation by waiting for a specified duration.

        This method simulates the primary function of the rack: holding tubes
        stationary within the magnetic field to allow paramagnetic beads
        to pellet against the tube wall. In a real-world scenario, this would
        be a blocking call that waits for the specified time before proceeding.

        Args:
            wait_duration_seconds: The time in seconds to wait for the beads
                                   to be fully separated and form a tight pellet.
        """
        call_machine_command("magrack_wait", {
            "time": wait_duration_seconds
        })
        

DEFAULT_MAGRACKP200_LOCATION = Location("magrack_P200")
class MagRackP200(BaseMachine, ABC):
    """
    Abstract base class for a magnetic separation rack for 200ul PCR tubes.

    This device uses high-performance permanent magnets to separate paramagnetic
    beads from a solution. The magnetic field is always active, requiring no
    external power. The primary operation involves placing tubes into the rack
    and waiting for a specified duration for the beads to form a tight pellet
    against the tube wall.
    """

    MODEL: str = "MS-08"
    NUM_SLOTS: int = 8
    
    def __init__(self, location: Location = DEFAULT_MAGRACKP200_LOCATION):
        super().__init__(location)

    def separate(self, duration_seconds: int = 60) -> None:
        """
        Waits for a specified duration to allow magnetic beads to separate.

        This method represents the core procedure of using the rack: allowing
        time for the permanent magnets to attract and immobilize the beads
        against the side of the tubes.

        Args:
            duration_seconds: The time in seconds to wait for complete bead
                              separation. Defaults to 60 seconds.
        """
        call_machine_command("magrack_wait", {
            "time": duration_seconds
        })
        
class TemperatureStep(TypedDict):
    """
    Defines a single temperature-hold step in a protocol.
    Example: {"temperature_celsius": 95.0, "duration_seconds": 180}
    """
    temperature_celsius: float
    duration_seconds: int

class Cycle(TypedDict):
    """
    Defines a cycle of multiple temperature steps to be repeated.
    Example: {
        "steps": [
            {"temperature_celsius": 95.0, "duration_seconds": 30},
            {"temperature_celsius": 60.0, "duration_seconds": 45}
        ],
        "count": 30
    }
    """
    steps: List[TemperatureStep]
    count: int

# A protocol is a list of individual steps or entire cycles.
ProtocolStep = Union[TemperatureStep, Cycle]

DEFAULT_THERMAL_CYCLER_LOCATION = Location("thermal_cycler")
# Do not support fluorescence detection
class ThermoCycler200ul(BaseMachine, abc.ABC):
    """
    An abstract interface for controlling a thermal cycler designed
    for standard 200ul PCR tubes or plates.
    """

    def __init__(self, location: Location = DEFAULT_THERMAL_CYCLER_LOCATION):
        """Initializes the ThermoCycler at a specific lab location."""
        super().__init__(location)

    def open_lid(self) -> None:
        """Opens the heated lid to allow for loading or unloading of plates."""
        call_machine_command("thermal_cycler_open_lid", {
        })

    def close_lid(self) -> None:
        """Closes the heated lid."""
        call_machine_command("thermal_cycler_close_lid", {
        })

    def run_protocol(self, protocol: List[ProtocolStep]) -> None:
        """
        Starts a thermal cycling protocol.
        The protocol can be simple isothermal incubation.

        The machine will execute the list of steps and cycles in order.

        Args:
            protocol: A list of TemperatureStep and Cycle dictionaries defining
                      the complete thermal cycling program.
        """
        call_machine_command("thermal_cycler_run_program", {
            "program": protocol
        })

    def pause(self) -> None:
        """Pauses the currently executing protocol."""
        pass

    def resume(self) -> None:
        """Resumes a paused protocol."""
        pass

    def stop(self) -> None:
        """
        Immediately stops the current protocol and cools the block to a safe
        standby temperature.
        """
        pass
    
DEFAULT_PIPETTE_LOCATION = Location("pipette")
class Pipette(BaseMachine, abc.ABC):
    """
    An abstract base class defining the interface for a robotic pipette.

    This interface is designed to be container-centric, where actions are
    performed on or between specified containers. Complexities like tip
    management are handled implicitly with sensible defaults to ensure
    a simple and intuitive user experience.
    """
    
    def __init__(self, location: Location = DEFAULT_PIPETTE_LOCATION):
        super().__init__(location)

    def transfer(
        self,
        volume: float, 
        source: Container,
        destination: Container,
        reuse_tip: bool = False,
        air_gap_volume: float = 0.0
    ) -> None:
        """
        Transfers a specified volume of liquid from a source to a destination.

        This method supports one-to-one, one-to-many (distribute),
        many-to-one (pool), and many-to-many transfers. By default, a new
        sterile tip is used for the entire operation and then discarded.

        Args:
        volume: The volume in microliters (uL) to transfer. Can be a
            single value for all transfers or a list of volumes
            corresponding to each source/destination pair.
        source: The container or list of containers to aspirate from.
        destination: The container or list of containers to dispense into.
        reuse_tip: If True, the pipette will not discard the tip after
            the operation is complete. Defaults to False.
        air_gap_volume: Volume of air in uL to aspirate after the liquid
                to prevent dripping. Defaults to 0.0.
        """
    # Validate that the transfer is possible before executing
        # replenishable source can be refilled automatically, otherwise check volume
        if source.volume < volume and not source.replenishable:
            raise ValueError(
            f"Insufficient volume in source {source.label}. "
            f"Required: {volume} uL, Available: {source.volume} uL."
        )
        if destination.volume + volume > destination.capacity:
            raise ValueError(
            f"Transfer will overflow destination {destination.label}. "
            f"Current Volume: {destination.volume} uL, Capacity: {destination.capacity} uL."
        )

        # Update the volumes in the software model
        source.volume -= volume
        destination.volume += volume

        # Send the command to the physical machine
        call_machine_command("pipette_move", {
            "dst_container_index": destination.index,
            "src_container_index": source.index,
            "volume": volume
        })

    def mix(
        self,
        volume: float,
        location: Container,
        repetitions: int,
        rate_per_minute: int = 20,
        reuse_tip: bool = False
    ) -> None:
        """
        Mixes the contents of a container by repeated aspiration and dispensing.

        A new tip is used by default and discarded upon completion.

        Args:
            volume: The volume in uL to aspirate and dispense during mixing.
            location: The container whose contents are to be mixed.
            repetitions: The number of mixing cycles to perform.
            rate_per_minute: The speed of the mix operation, in cycles per
                             minute. Defaults to 20.
            reuse_tip: If True, the pipette will not discard the tip after
                       the operation is complete. Defaults to False.
        """
        call_machine_command("pipette_mix", {
            "container_index": location.index,
            "num": repetitions,
            "volume": volume,
            "speed": rate_per_minute
        })
    
DEFAULT_ROBOT_LOCATION = Location("robot")
class Robot(BaseMachine, abc.ABC):
    """
    An abstract base class defining the interface for a laboratory robot arm.

    The API is designed to be container-centric, meaning that all primary
    operations are defined in terms of actions on Container objects.
    """
    def __init__(self, location: Location = DEFAULT_ROBOT_LOCATION):
        super().__init__(location)
        
    def home(self) -> None:
        """
        Initializes and moves the robot to a safe, known home position.

        This is typically required after powering on the device or before
        starting a new run to ensure correct calibration.
        """
        pass

    def move_container(self, container: Container, destination: Location) -> None:
        """
        Moves a single container from its current location to a new destination.

        This high-level command encapsulates the sequence of picking up,
        transporting, and placing the container. The implementation should
        update the container's `.location` attribute upon successful completion.

        Args:
            container: The container object to be moved. The robot uses the
                       container's current `.location` as the source.
            destination: The target location where the container will be placed.
        """
    
        call_machine_command("robot_move_container", {
            "dst_pos": destination.description,
            "container_index": container.index
        })
        
    def open_port(self, port: Port) -> None:
        """
        Opens a specified port on a machine.

        Args:
            port: The Port object representing the port to be opened.
        """
        call_machine_command("open_port", {
            "port": port.port_type.name
        })

    def close_port(self, port: Port) -> None:
        """
        Closes a specified port on a machine.

        Args:
            port: The Port object representing the port to be closed.
        """
        call_machine_command("close_port", {
            "port": port.port_type.name
        })

DEFAULT_SEQUENCER_LOCATION = Location("sequencer")
class Sequencer(abc.ABC):
    """
    An abstract base class defining a simple, universal interface for
    controlling a DNA/RNA sequencer.

    This interface is designed to be minimal and intuitive, focusing on the
    three core actions of a sequencing workflow: starting, monitoring,
    and stopping a run.
    """
    def __init__(self, location: Location = DEFAULT_SEQUENCER_LOCATION):
        self.location = location

    def start_run(
        self, run_name: str, output_directory: str = "."
    ) -> None:
        """
        Begins a new sequencing run.

        This method assumes the device has been physically prepared with a
        flow cell and a prepared sample library.

        Args:
            run_name: A unique identifier for the sequencing run.
            output_directory: The path to a directory where sequencing
                              data (e.g., FASTQ files) will be written in
                              real-time. The directory will be created if
                              it does not exist. Defaults to the current
                              directory ('.').

        Raises:
            RuntimeError: If a run is already in progress or the device
                          is not ready.
        """
        call_machine_command("start_sequencing",{
            "run_name": run_name,
            "output_directory": output_directory
        })

    def stop_run(self) -> None:
        """
        Stops the currently active sequencing run gracefully.

        If a run is in progress, this command will terminate the sequencing
        process and finalize any data output. If no run is active, this
        method does nothing.
        """
        pass

DEFAULT_REFRIGERATOR_LOCATION = Location("refrigerator")
class Refrigerator(BaseMachine, ABC):
    """
    Abstract base class representing a simple, low-temperature storage unit.

    This API models the refrigerator as a passive storage environment. In line
    with the "Container-Centric Design" principle, the refrigerator does not
    have "place" or "retrieve" methods. Such actions are performed *on* a
    Container by an external agent (e.g., a robotic arm), which changes the
    container's location to be inside the refrigerator. This class provides
    methods to monitor and control the environment and to query its contents.
    """

    def __init__(self, target_temperature: float = 4.0, location: Location = DEFAULT_REFRIGERATOR_LOCATION):
        """
        Initializes the Refrigerator.

        Args:
            location: The physical location of the refrigerator.
            target_temperature: The default target temperature in Celsius.
        """
        self.location = location
        self.target_temperature = target_temperature

    def get_current_temperature(self) -> float:
        """
        Returns the current internal temperature of the refrigerator in Celsius.
        """
        return self.target_temperature

    def get_contents(self) -> List[Container]:
        """
        Returns a list of all containers currently stored inside the refrigerator.
        """
        pass
    
    def set_target_temperature(self, celsius: float):
        """
        Sets the target temperature for the refrigerator's environment.

        Args:
            celsius: The desired target temperature in Celsius.
        """
        self.target_temperature = celsius
        pass
# Initialize all of the instruments, use directly
timer = Timer()
container_manager = ContainerManager()
pipette = Pipette()
robot = Robot()
capper = Capper_200ul_tubes()
centrifuge_1p5mL = Centrifuge1p5mL()
centrifuge_200uL = Centrifuge_200ulTubes()
fluorometer = Fluorometer200ul()
heater_1p5mL = Heater1_5mlTubes()
heater_shaker = HeaterShaker200uL()
mag_rack_1p5mL = MagRackP1500()
mag_rack_200uL = MagRackP200()
thermal_cycler = ThermoCycler200ul()
sequencer = Sequencer()
refrigerator = Refrigerator()
