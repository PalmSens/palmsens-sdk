from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional

from PalmSens import Fitting as PSFitting
from System import Array

from ._data.curve import Curve
from ._data.eisdata import EISData

if TYPE_CHECKING:
    from matplotlib import fig


@dataclass(slots=True)
class Parameter:
    """Set or update Parameter attributes."""

    symbol: str
    """Name of the parameter (not used in minimization)."""
    value: Optional[float] = None
    """Initial value of the parameter."""
    min: Optional[float] = None
    """Minimum (lower bound) for the parameter."""
    max: Optional[float] = None
    """Maximum (upper bound) for the parameter."""
    fixed: Optional[bool] = None
    """If True, fix the value for this parameter."""

    @classmethod
    def _from_psparameter(cls, psparameter: PSFitting.Parameter):
        """Create instance from SDK Parameter object."""
        return cls(
            symbol=psparameter.Symbol,
            value=psparameter.Value,
            min=psparameter.MinValue,
            max=psparameter.MaxValue,
            fixed=psparameter.Fixed,
        )

    def _update_psparameter(self, psparameter: PSFitting.Parameter):
        """Update PalmSens SDK object with values from dataclass."""
        if self.value:
            psparameter.Value = self.value
        if self.min:
            psparameter.MinValue = self.min
        if self.max:
            psparameter.MaxValue = self.max
        if self.fixed:
            psparameter.Fixed = self.fixed


class Parameters(Sequence):
    """Tuple-like container class for parameters.

    This class is instantiated from the CDC code and contains
    default parameters. This ensures that the length and type of
    parameters match that of `CircuitModel`. Update the parameters
    in this class and pass to `CircuitModel.fit()`.

    Parameters
    ----------
    cdc: str
        Genererate fitting parameters for this CDC.
    """

    def __init__(self, cdc: str):
        self.cdc = cdc
        """CDC code used to generate parameter listing."""

        model = PSFitting.Models.CircuitModel()
        model.SetCircuit(cdc)
        self._parameters = tuple(
            Parameter._from_psparameter(psparam) for psparam in model.InitialParameters
        )

    def __len__(self):
        return len(self._parameters)

    def __getitem__(self, key):
        return self._parameters[key]

    def __repr__(self) -> str:
        return self._parameters.__repr__()

    def __str__(self) -> str:
        return self._parameters.__str__()

    def _update_psmodel_parameters(self, psmodel: PSFitting.Models.CircuitModel) -> None:
        """Update the initial parameters in the SDK model with parameters in this instance.

        Note that the length and type of parameters must match that of the SDK class.
        """
        if len(self) != psmodel.NParameters:
            raise ValueError(f'Parameters must be of length {psmodel.NParameters}')

        for param, psparam in zip(self, psmodel.InitialParameters):
            param._update_psparameter(psparam)


@dataclass(frozen=True)
class FitResult:
    """Container for fitting results."""

    cdc: str
    """Circuit model CDC values."""
    parameters: list[float]
    """Optimized parameters for CDC."""
    error: list[float]
    """Error (%) on parameters."""
    chisq: float
    """Chi-squared goodness of fit statistic."""
    n_iter: int
    """Total number of iterations."""
    exit_code: str
    """Exit code for the minimization."""

    @classmethod
    def from_psfitresult(cls, result: PSFitting.FitResult, cdc: str):
        """Construct fitresult from SDK FitResult."""
        return cls(
            cdc=cdc,
            chisq=result.ChiSq,
            exit_code=result.ExitCode.ToString(),
            n_iter=result.NIterations - 1,
            parameters=list(result.FinalParameters),
            error=list(result.ParameterSDs),
        )

    @classmethod
    def from_eisdata(cls, data: EISData):
        """Construct fitresulf from EISData."""
        return cls(
            cdc=data.cdc,
            parameters=data.cdc_values,
            chisq=0,
            error=[0.0 for _ in data.cdc_values],
            exit_code='',
            n_iter=0,
        )

    def get_psmodel(self, data: EISData) -> PSFitting.Models.CircuitModel:
        """Get SDK Circuit model object"""
        psmodel = PSFitting.Models.CircuitModel()
        psmodel.SetEISdata(data._pseis)
        psmodel.SetCircuit(self.cdc)
        psmodel.SetInitialParameters(self.parameters)
        return psmodel

    def get_nyquist(self, data: EISData) -> tuple[Curve, Curve]:
        """Calculate observed and calculated nyquist curves.

        Parameters
        ----------
        data : EISData
            Input EIS data.

        Returns
        -------
        calc, meas : tuple[Curve, Curve]
            Returns the nyquist curve calculated from the model parameters
            and the measured curve from the EIS data.
        """
        psmodel = self.get_psmodel(data=data)
        curves = psmodel.GetNyquist()
        calc, meas = (Curve(pscurve=pscurve) for pscurve in curves)
        return calc, meas

    def get_bode_z(self, data: EISData) -> tuple[Curve, Curve]:
        """Calculate observed and calculated Bode curve Z vs Frequency.

        Parameters
        ----------
        data : EISData
            Input EIS data.

        Returns
        -------
        calc, meas : tuple[Curve, Curve]
            Returns the nyquist curve calculated from the model parameters
            and the measured curve from the EIS data.
        """
        psmodel = self.get_psmodel(data=data)
        curves = psmodel.GetCurveZabsOverFrequency(False)
        calc, meas = (Curve(pscurve=pscurve) for pscurve in curves)
        return calc, meas

    def get_bode_phase(self, data: EISData) -> tuple[Curve, Curve]:
        """Calculate observed and calculated Bode curve phase vs Frequency.

        Parameters
        ----------
        data : EISData
            Input EIS data.

        Returns
        -------
        calc, meas : tuple[Curve, Curve]
            Returns the nyquist curve calculated from the model parameters
            and the measured curve from the EIS data.
        """
        psmodel = self.get_psmodel(data=data)
        curves = psmodel.GetCurvePhaseOverFrequency(False)
        calc, meas = (Curve(pscurve=pscurve) for pscurve in curves)
        return calc, meas

    def plot_nyquist(self, data: EISData) -> fig.Figure:
        """Make nyquist plot.

        Parameters
        ----------
        data : EISData
            Input EIS data.

        Returns
        -------
        fig : fig.Figure
            Returns matplotlib figure object. use `fig.show()` to render plot.
        """
        import matplotlib.pyplot as plt

        calc, meas = self.get_nyquist(data=data)
        fig, ax = plt.subplots()
        ax.set_title('Nyquist plot')

        calc.plot(ax=ax)
        meas.plot(ax=ax, marker='^', linestyle='None')

        return fig

    def plot_bode(self, data: EISData) -> fig.Figure:
        """Make bode plot.

        Parameters
        ----------
        data : EISData
            Input EIS data.

        Returns
        -------
        fig : fig.Figure
            Returns matplotlib figure object. use `fig.show()` to render plot.
        """
        import matplotlib.pyplot as plt

        calc_z, meas_z = self.get_bode_z(data=data)
        calc_ph, meas_ph = self.get_bode_phase(data=data)
        fig, ax1 = plt.subplots()
        ax1.set_title('Bode plot')
        ax1.set_xscale('log')

        calc_z.plot(ax=ax1, legend=False, color='C0')
        meas_z.plot(ax=ax1, marker='^', linestyle='None', color='C0', legend=False)

        ax2 = ax1.twinx()
        calc_ph.plot(ax=ax2, legend=False, color='C1')
        meas_ph.plot(ax=ax2, marker='^', linestyle='None', color='C1', legend=False)

        fig.legend()
        return fig


@dataclass
class CircuitModel:
    """Fit an equivalent circuit model.

    The class takes a CDC string as a required argument to set up the model.

    The other parameters are optional and can be used to tweak the minimization.
    The model supports fitting over a specified frequency range and adjustment of exit
    conditions (i.e. max # iterations, min delta error, min parameter step
    size).

    Optionally you can change the initial values of the parameters, their
    min/max bounds or fix their value.

    Example:

    ```
    model = CircuitModel('R(RC)')
    result = model.fit(eis_data)
    ```
    """

    cdc: str
    """Sets the circuit specified in the CDC string.

    For more information, see:
        https://www.utwente.nl/en/tnw/ims/publications/downloads/cdc-explained.pdf
    """

    algorithm: Literal['leastsq', 'nelder-mead'] = 'leastsq'
    """Name of the fitting method to use.

    Valid values are: `leastsq` (Levenberg-Marquardt), `nelder-mead`
    """

    max_iterations: int = 500
    """Maximum number of iterations.

    Minimization terminates once it reaches this number of steps (default = 500).
    """

    min_delta_error: float = 1.0e-9
    """Minimum convergence error.

    Minimization converges if the residual (squared difference)
        falls below this value (default = 1e-9).
    """

    min_delta_step: float = 1.0e-12
    """Minimum convergence step.

    Minimization converges if the difference in parameter values
        falls below this value (default = 1e-12)."""

    min_freq: Optional[float] = None
    """Minimum fitting frequency in Hz."""

    max_freq: Optional[float] = None
    """Maximum fitting frequency in Hz."""

    tolerance: float = 1e-4
    """Convergence tolerance. Nelder-Mead only (default = 1e-4)."""

    lambda_start: float = 0.01
    """Start lambda value. Levenberg-Marquardt only (default = 0.01)."""

    lambda_factor: float = 10.00
    """Lambda Scaling Factor. Levenberg-Marquardt only (default = 10)."""

    _last_result: Optional[FitResult] = None
    _last_psfitter: Optional[PSFitting.FitAlgorithm] = None

    def default_parameters(self) -> Parameters:
        """Get default parameters. Use this to modify parameter values.

        Returns
        -------
        parameters : Parameters
            Default parameters for CDC.
        """
        return Parameters(self.cdc)

    def _psfitoptions(
        self,
        data: EISData,
        *,
        parameters: Optional[Sequence[float] | Parameters] = None,
    ) -> PSFitting.FitOptions:
        """Fit circuit model.

        Parameters
        ----------
        data : EISData
            Input EIS data.
        parameters : Optional[Sequence[float] | Parameters]
            Optional initial parameters for fit. Can be passed as
            `Parameters` object or list of values.

        Returns
        -------
        opts : PSFitting.FitOptions
            SDK object containing fitting options.
        """
        model = PSFitting.Models.CircuitModel()
        model.SetCircuit(self.cdc)
        model.SetEISdata(data._pseis)

        if parameters:
            if isinstance(parameters, Parameters):
                if self.cdc != parameters.cdc:
                    raise ValueError(
                        f'Parameters cdc ({self.cdc}) does not match Model ({parameters.cdc})'
                    )
                parameters._update_psmodel_parameters(model)
            else:
                if len(parameters) != model.NParameters:
                    raise ValueError(f'Parameters must be of length {model.NParameters}')
                model.SetInitialParameters(parameters)

        opts = PSFitting.FitOptionsCircuit()
        opts.Model = model
        opts.RawData = data._pseis

        opts.MaxIterations = self.max_iterations
        opts.MinimumDeltaErrorTerm = self.min_delta_error
        opts.MinimumDeltaParameters = self.min_delta_step

        if self.min_freq or self.max_freq:
            self.min_freq = self.min_freq or 0
            self.max_freq = self.max_freq or 0

            array = data.dataset.freq_arrays()[-1]
            sel = (self.min_freq < val < self.max_freq for val in array)

            opts.SelectedDataPoints = Array[bool]((bool(_) for _ in sel))

        return opts

    @property
    def last_result(self):
        """Store last fit result."""
        return self._last_result

    @property
    def last_psfitter(self):
        """Store reference to last SDK fitting object."""
        return self._last_psfitter

    def fit(
        self, data: EISData, *, parameters: Optional[Sequence[float] | Parameters] = None
    ) -> FitResult:
        """Fit circuit model.

        Parameters
        ----------
        data : EISData
            Input data.
        parameters : Optional[Sequence[float] | Parameters]
            Optional initial parameters for fit. Can be passed as
            `Parameters` object or list of values.

        Returns
        -------
        result : FitResult
            Returns dataclass with fit results. Can also be accessed via `.last_result`.
        """
        if not data.frequency_type == 'Scan':
            raise ValueError(
                f'Fit only supports EIS scans at a fixed potential, got {data.frequency_type=}.'
            )
        if not data.scan_type == 'Fixed':
            raise ValueError(
                f'Fit only supports EIS scans at a fixed potential, got {data.scan_type=}.'
            )

        opts = self._psfitoptions(data=data, parameters=parameters)

        fitter = PSFitting.FitAlgorithm.FromAlgorithm(opts)
        fitter.ApplyFitCircuit()
        self._last_psfitter = fitter
        self._last_result = FitResult.from_psfitresult(fitter.FitResult, cdc=self.cdc)
        return self._last_result
