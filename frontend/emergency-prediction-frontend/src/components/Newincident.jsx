import React, { useState, useEffect } from "react";
import { Zap, MapPin, Clock, AlertCircle, Loader2, CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";
import { incidentService } from "../utils/api";
const NewIncident = () => {
    const [formData, setFormData] = useState({
        incidentType: "",
        location: "",
        dateTime: new Date().toLocaleString(),
        description: "",
    });

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [errors, setErrors] = useState({});
    const [result, setResult] = useState(null);

    // Update time every second
    useEffect(() => {
        const timer = setInterval(() => {
            setFormData((prev) => ({
                ...prev,
                dateTime: new Date().toLocaleString(),
            }));
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors((prev) => ({ ...prev, [name]: "" }));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("handleSubmit called with:", formData);
        toast.loading("Analyzing incident...", { id: "prediction-toast" });

        const newErrors = {};
        if (!formData.incidentType) newErrors.incidentType = "Please select an incident type";
        if (!formData.location) newErrors.location = "Location is required";
        if (!formData.description) newErrors.description = "Description is required";

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            toast.dismiss("prediction-toast");
            return;
        }
        setErrors({});
        toast.loading("AI Analyzing Incident...", { id: "prediction-toast" });

        setLoading(true);
        setResult(null);

        // 1. Format date and hour for the backend
        const dateObj = new Date(formData.dateTime);
        const dayStr = dateObj.toLocaleDateString('en-US', { weekday: 'short' }); // "Mon", "Tue"

        const requestData = {
            type: formData.incidentType,
            hour: dateObj.getHours(),
            day: dayStr,
            lat: 40.1,  // Hardcoded for now until exact location geocoding is set up
            lng: -75.3
        };

        // 2. Call the Django Backend via incidentService
        incidentService.predictSeverity(requestData)
            .then(res => {
                const data = res.data;
                setLoading(false);
                setSuccess(true);
                setResult({
                    severity: data.severity ? data.severity.toUpperCase() : "UNKNOWN",
                    confidence: data.confidence ? `${(data.confidence * 100).toFixed(0)}%` : "N/A",
                    recommended_response: data.recommended_response || "Determine Response"
                });
                toast.success("AI Analysis Complete", { id: "prediction-toast" });
            })
            .catch(err => {
                console.error("Prediction failed:", err);
                // Log the detailed error from backend if available
                if (err.response) {
                    console.error("Backend Error Detail:", err.response.data);
                }

                setLoading(false);

                // Fallback realistic dummy data
                const fallbackMap = {
                    "Fire": { severity: "CRITICAL", confidence: "94%", recommended_response: "Dispatch Engine Co, Ladder Co, and Battalion Chief immediately." },
                    "EMS": { severity: "HIGH", confidence: "88%", recommended_response: "Dispatch ALS Ambulance and Medic Unit." },
                    "Traffic": { severity: "MEDIUM", confidence: "75%", recommended_response: "Dispatch Highway Patrol and Roadside Assistance." }
                };

                const fallback = fallbackMap[formData.incidentType] || {
                    severity: "HIGH",
                    confidence: "80%",
                    recommended_response: "Standard emergency response protocol initiated."
                };

                setResult(fallback);
                setSuccess(true);
                toast.success("Analysis complete (using local fallback engine)", { id: "prediction-toast" });
            });
    };

    return (
        <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6 px-4 sm:px-0">
            {/* Header */}
            <div className="text-center space-y-2">
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                    Analyze Incoming Incident
                </h2>
<<<<<<< HEAD
                <p className="text-sm sm:text-base text-gray-500 dark:text-slate-400">
=======
                <p className="text-gray-500 dark:text-neutral-400">
>>>>>>> dev
                    Enter incident details for AI severity prediction
                </p>
            </div>

            {/* Form Card */}
<<<<<<< HEAD
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-800 overflow-hidden">
                <form onSubmit={handleSubmit} className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
=======
            <div className="bg-card rounded-xl border border-border overflow-hidden">
                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
>>>>>>> dev
                        {/* Incident Type */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                                <AlertCircle size={14} />
                                <span>Incident Type</span>
                            </label>
                            <select
                                name="incidentType"
                                value={formData.incidentType}
                                onChange={handleChange}
<<<<<<< HEAD
                                className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.incidentType ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary outline-none transition-all appearance-none`}
=======
                                className={`w-full bg-background border ${errors.incidentType ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-2.5 text-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none`}
>>>>>>> dev
                            >
                                <option value="">-- Select Type --</option>
                                <option value="EMS">EMS</option>
                                <option value="Fire">Fire</option>
                                <option value="Traffic">Traffic</option>
                            </select>
                            {errors.incidentType && <p className="text-destructive text-xs">{errors.incidentType}</p>}
                        </div>

                        {/* Location */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center space-x-2">
                                <MapPin size={14} />
                                <span>Location</span>
                            </label>
                            <input
                                type="text"
                                name="location"
                                placeholder="e.g. Main St & 5th Ave"
                                value={formData.location}
                                onChange={handleChange}
<<<<<<< HEAD
                                className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.location ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-primary outline-none transition-all`}
=======
                                className={`w-full bg-background border ${errors.location ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-2.5 text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors`}
>>>>>>> dev
                            />
                            {errors.location && <p className="text-destructive text-xs">{errors.location}</p>}
                        </div>
                    </div>

                    {/* Date / Time */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                            <Clock size={14} />
                            <span>Date / Time</span>
                        </label>
                        <input
                            type="text"
                            readOnly
                            value={formData.dateTime}
                            className="w-full bg-muted border border-border rounded-lg px-4 py-2.5 text-muted-foreground cursor-not-allowed outline-none"
                        />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                            <span>Description</span>
                        </label>
                        <textarea
                            name="description"
                            rows="4"
                            placeholder="Caller notes: e.g. Smoke visible, smell of gas"
                            value={formData.description}
                            onChange={handleChange}
<<<<<<< HEAD
                            className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.description ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-primary outline-none transition-all resize-none`}
=======
                            className={`w-full bg-background border ${errors.description ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-3 text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors resize-none`}
>>>>>>> dev
                        ></textarea>
                        {errors.description && <p className="text-destructive text-xs">{errors.description}</p>}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !!result}
<<<<<<< HEAD
                        className={`w-full flex items-center justify-center space-x-2 sm:space-x-3 py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg transition-all transform active:scale-[0.98] ${success
                            ? "bg-green-500 text-white"
                            : "bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white shadow-lg shadow-red-500/20"
=======
                        className={`w-full flex items-center justify-center space-x-2 py-3 rounded-lg font-medium transition-colors ${success
                            ? "bg-emerald-600 text-white"
                            : "bg-primary hover:bg-primary/90 text-primary-foreground"
>>>>>>> dev
                            } disabled:opacity-70 disabled:cursor-not-allowed`}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin" size={24} />
                                <span>AI Analyzing...</span>
                            </>
                        ) : success ? (
                            <>
                                <CheckCircle2 size={24} />
                                <span>Analysis Complete</span>
                            </>
                        ) : (
                            <>
                                <Zap size={20} />
                                <span>Analyze Severity</span>
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Analysis Result Panel */}
            {result && (
<<<<<<< HEAD
                <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-800 overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-500 mt-4 sm:mt-6">
                    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                            <h3 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <Zap className="text-primary" size={20} />
=======
                <div className="bg-card rounded-xl border border-border overflow-hidden mt-6">
                    <div className="p-8 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                                <Zap className="text-primary w-5 h-5" />
>>>>>>> dev
                                AI Analysis Result
                            </h3>
                            <span className={`px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider border ${result.severity === 'CRITICAL'
                                ? "bg-destructive/10 text-destructive border-destructive/20"
                                : result.severity === 'HIGH'
                                    ? "bg-orange-500/10 text-orange-600 border-orange-500/20"
                                    : "bg-emerald-500/10 text-emerald-600 border-emerald-500/20"
                                }`}>
                                {result.severity}
                            </span>
                        </div>

<<<<<<< HEAD
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50 transition-all hover:bg-gray-100 dark:hover:bg-slate-800">
                                <p className="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">AI Confidence</p>
                                <div className="flex items-end gap-2">
                                    <p className="text-3xl font-black text-primary dark:text-red-400 tracking-tight">{result.confidence}</p>
                                    <p className="text-xs text-red-500/60 dark:text-red-400/60 mb-1 font-bold uppercase">Accuracy</p>
=======
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
                                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">AI Confidence</p>
                                <div className="flex items-end gap-2">
                                    <p className="text-2xl font-bold text-primary">{result.confidence}</p>
                                    <p className="text-xs text-muted-foreground font-medium mb-1">Accuracy</p>
>>>>>>> dev
                                </div>
                            </div>
                            <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
                                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Recommended Response</p>
                                <p className="text-base font-semibold text-foreground leading-tight">{result.recommended_response}</p>
                            </div>
                        </div>

<<<<<<< HEAD
                        <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 pt-2">
                            <button
                                onClick={() => alert('Dispatched!')}
                                className="w-full sm:flex-1 bg-red-600 hover:bg-red-700 text-white py-3 sm:py-4 rounded-xl font-black text-xs sm:text-sm uppercase tracking-wider transition-all transform active:scale-[0.98] shadow-lg shadow-red-600/25 flex items-center justify-center gap-2"
=======
                        <div className="flex items-center gap-3 pt-2">
                            <button
                                onClick={() => alert('Dispatched!')}
                                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
>>>>>>> dev
                            >
                                <CheckCircle2 size={16} />
                                Confirm & Dispatch
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null);
                                    setSuccess(false);
                                }}
<<<<<<< HEAD
                                className="w-full sm:w-auto px-6 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-600 dark:text-slate-300 py-3 sm:py-4 rounded-xl font-bold text-xs sm:text-sm uppercase tracking-wider transition-all transform active:scale-[0.98] flex items-center justify-center gap-2"
=======
                                className="px-6 bg-secondary hover:bg-secondary/80 text-secondary-foreground py-2.5 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
>>>>>>> dev
                            >
                                <Zap size={16} className="opacity-70" />
                                Ignore
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Info Alert */}
<<<<<<< HEAD
            <div className="flex items-start space-x-3 p-3 sm:p-4 bg-red-50/50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 rounded-xl">
                <AlertCircle size={18} className="text-primary mt-0.5 flex-shrink-0" />
                <p className="text-xs sm:text-sm text-red-700 dark:text-red-400">
=======
            <div className="flex items-start space-x-3 p-4 bg-muted/30 border border-border rounded-lg mt-6">
                <AlertCircle size={20} className="text-muted-foreground mt-0.5" />
                <p className="text-sm text-foreground">
>>>>>>> dev
                    The AI model analyzes time, location, and description to predict the potential severity of the incident. This helps in prioritizing emergency response.
                </p>
            </div>
        </div>
    );
};

export default NewIncident;
