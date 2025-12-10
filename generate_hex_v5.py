import re
import binascii
import json

# JS Logic V5 (Uses data-var)
# JS Logic V5.1 (Reactive Auto-Calc)
js_logic = r"""
window.ozExecuteCalc = function(target) {
    // Handle both Button and Container triggers
    var container = target.hasAttribute('data-itb-calculator') ? target : target.closest('[data-itb-calculator]');
    if (!container) return;

    var id = container.getAttribute('data-itb-calculator');
    var func = window.OZ_FORMULAS[id];
    if (!func) return console.error('No formula for ' + id);

    var inputs = container.querySelectorAll('[data-var]');
    var values = {};
    inputs.forEach(function(inp) {
        var key = inp.getAttribute('data-var');
        var val = inp.value;
        if (inp.tagName === 'SELECT') {
            values[key] = val;
        } else {
            values[key] = parseFloat(val) || 0;
        }
    });

    try {
        var result = func(values);
        var outContainer = container.querySelector('.itb-outputs');
        if (!outContainer) return;

        // Mapping Mode
        for (var key in result) {
            var el = outContainer.querySelector('[data-itb-output="' + key + '"]');
            if (el) {
                var val = result[key];
                var fmt = el.getAttribute('data-itb-format');
                
                if (fmt === 'currency') {
                    if (!isNaN(parseFloat(val))) val = '$' + parseFloat(val).toFixed(2);
                } else if (fmt === 'percent') {
                    if (!isNaN(parseFloat(val))) val = parseFloat(val).toFixed(1) + '%';
                }

                el.innerText = val;
            }
        }
        outContainer.style.display = 'block';
    } catch(e) {
        console.error(e);
    }
};

window.OZ_FORMULAS = window.OZ_FORMULAS || {};
Object.assign(window.OZ_FORMULAS, {
    // 1. Bottling Line Capacity Calculator
    "capacity-calculator-2026": function(v) {
        var dailyProductionTarget = parseFloat(v.dailyProductionTarget);
        var operatingHoursPerDay = parseFloat(v.operatingHoursPerDay);
        var operatingDaysPerYear = parseFloat(v.operatingDaysPerYear);
        var plannedDowntimePercentage = parseFloat(v.plannedDowntimePercentage);

        var effectiveOperatingHours = operatingHoursPerDay * (1 - plannedDowntimePercentage / 100);
        var requiredBPH = Math.ceil(dailyProductionTarget / effectiveOperatingHours);
        var annualCapacity = dailyProductionTarget * operatingDaysPerYear;
        var recommendedBPH = Math.ceil(requiredBPH * 1.15);
        var utilizationRate = (requiredBPH / recommendedBPH) * 100;

        return {
            requiredBPH: requiredBPH,
            recommendedBPH: recommendedBPH,
            annualCapacity: annualCapacity,
            utilizationRate: utilizationRate.toFixed(1)
        };
    },

    // 2. TCO Calculator (TIJ vs Laser)
    "tco-calculator-2026": function(v) {
        var dailyProduction = parseFloat(v.dailyProduction);
        var daysPerYear = parseFloat(v.daysPerYear);
        var tijCost = parseFloat(v.tijCost);
        var printsPerCart = parseFloat(v.printsPerCart);
        var laserCapex = parseFloat(v.laserCapex);
        var yearsAmort = parseFloat(v.yearsAmort);

        var annualVolume = dailyProduction * daysPerYear;
        var tijAnnualCost = (annualVolume / printsPerCart) * tijCost;
        var laserAnnualAmort = laserCapex / yearsAmort;
        var laserOpEx = 500; // Fixed OpEx assumption
        var laserTotalAnnual = laserAnnualAmort + laserOpEx;
        // var tijCostPerPrint = tijCost / printsPerCart; // Not displayed
        var savings = Math.abs(tijAnnualCost - laserTotalAnnual);

        return {
            annualVolume: annualVolume,
            tijAnnualCost: tijAnnualCost.toFixed(2),
            laserTotalAnnual: laserTotalAnnual.toFixed(2),
            savings: savings.toFixed(2)
        };
    },

    // 3. Energy Cost Calculator
    "energy-cost-calculator-2026": function(v) {
        var lineSpeed = parseFloat(v.lineSpeed); // BPH
        var energyConsumptionOld = parseFloat(v.energyConsumptionOld); // kWh/1k
        var energyConsumptionNew = parseFloat(v.energyConsumptionNew); // kWh/1k
        var electricityCost = parseFloat(v.electricityCost);
        var operatingHours = parseFloat(v.operatingHours);

        var annualBottlesOld = lineSpeed * operatingHours;
        var annualEnergyOld = (annualBottlesOld / 1000) * energyConsumptionOld;
        var annualEnergyNew = (annualBottlesOld / 1000) * energyConsumptionNew;
        var annualEnergySavings = annualEnergyOld - annualEnergyNew;
        var annualCostSavings = annualEnergySavings * electricityCost;
        var savingsPercentage = ((annualEnergyOld - annualEnergyNew) / annualEnergyOld) * 100;

        return {
            annualEnergySavings: Math.round(annualEnergySavings),
            annualCostSavings: annualCostSavings.toFixed(2),
            savingsPercentage: savingsPercentage.toFixed(1)
        };
    },

    // 4. Incoterms Cost Calculator
    "incoterms-cost-calculator-2026": function(v) {
        var fobPrice = parseFloat(v.fobPrice);
        var freightCost = parseFloat(v.freightCost);
        var insuranceRate = parseFloat(v.insuranceRate);
        var customsDutyRate = parseFloat(v.customsDutyRate);
        var customsBrokerFee = parseFloat(v.customsBrokerFee);

        var cifBeforeInsurance = fobPrice + freightCost;
        var insuranceCost = cifBeforeInsurance * (insuranceRate / 100);
        var cifPrice = cifBeforeInsurance + insuranceCost;
        var customsDuty = cifPrice * (customsDutyRate / 100);
        var totalLandedCost = cifPrice + customsDuty + customsBrokerFee;
        var additionalCostPercentage = ((totalLandedCost - fobPrice) / fobPrice) * 100;

        return {
            cifPrice: cifPrice.toFixed(2),
            customsDuty: customsDuty.toFixed(2),
            totalLandedCost: totalLandedCost.toFixed(2),
            additionalCostPercentage: additionalCostPercentage.toFixed(1)
        };
    },

    // 5. ROI Payback Calculator
    "roi-payback-calculator-2026": function(v) {
        var equipmentInvestment = parseFloat(v.equipmentInvestment);
        var annualSavings = parseFloat(v.annualSavings);
        var operatingYears = parseFloat(v.operatingYears);
        var taxRate = parseFloat(v.taxRate);
        var maintenanceCost = parseFloat(v.maintenanceCost);

        var netAnnualSavings = annualSavings - maintenanceCost;
        var afterTaxAnnualProfit = netAnnualSavings * (1 - taxRate / 100);
        var totalAfterTaxProfit = afterTaxAnnualProfit * operatingYears;
        
        var roi = ((totalAfterTaxProfit - equipmentInvestment) / equipmentInvestment) * 100;
        var paybackPeriod = equipmentInvestment / afterTaxAnnualProfit;
        var annualROI = (afterTaxAnnualProfit / equipmentInvestment) * 100;

        return {
            afterTaxAnnualProfit: afterTaxAnnualProfit.toFixed(2),
            paybackPeriod: paybackPeriod.toFixed(1),
            roi: roi.toFixed(1),
            annualROI: annualROI.toFixed(1)
        };
    },

    // --- PHASE 2: LEGACY TOOLS ---

    // 6. PG Estimator
    "pg-estimator-class3": function(v) {
        var fp = parseFloat(v.fp);
        var ibp = parseFloat(v.ibp);
        var pg = "Review";
        var comment = "Check regulations";

        if (fp < 23 && ibp <= 35) {
            pg = "I";
            comment = "Top Hazard (Boiling < 35°C)";
        } else if (fp < 23 && ibp > 35) {
            pg = "II";
            comment = "Standard Flammable (FP < 23°C)";
        } else if (fp >= 23 && fp <= 60) {
            pg = "III";
            comment = "Low Flammability (FP 23-60°C)";
        }

        return { pg: pg, comment: comment };
    },

    // 7. SDS Version Compare
    "sds-version-compare": function(v) {
        return {
            note: "Audit: SDS Rev " + v.rev + " confirmed. FP=" + v.fp + "C, IBP=" + v.ibp + "C."
        };
    },

    // 8. UN 4G Decoder
    "un-4g-code-decoder": function(v) {
        // e.g., 4G/Y25/S/25/USA/+ID
        var parts = v.code.split('/');
        if (parts.length < 5) return { explain: "Invalid Code Format" };
        
        var type = parts[0]; // 4G
        var perf = parts[1]; // Y25
        var pg = perf.charAt(0) === 'X' ? 'I/II/III' : (perf.charAt(0) === 'Y' ? 'II/III' : 'III');
        var gross = perf.substring(1);
        var solid = parts[2] === 'S' ? 'Solids/Inner-Packagings' : 'Liquids (Pressure Tested)';
        
        return {
            explain: "Type: " + type + ", PG: " + pg + ", Max Gross: " + gross + "kg, Content: " + solid
        };
    },

    // 9. LQ Eligibility Checker
    "lq-eligibility-checker": function(v) {
        var m = v.mode;
        var p = v.pg;
        var ml = parseFloat(v.inner_ml);
        var ok = "No";
        var mark = "None";

        if (m.indexOf('Ground') !== -1) {
            if ((p === 'I' && ml <= 500) || (p === 'II' && ml <= 1000) || (p === 'III' && ml <= 5000)) {
                ok = "Yes"; mark = "LQ Diamond";
            }
        } else if (m === 'Air') {
            if (p !== 'I' && ml <= 1000) { // Rough heuristic
                ok = "Maybe (Y-LQ)"; mark = "Y-LQ Diamond";
            }
        } else if (m === 'Sea') {
            if (ml <= 1000 && (p === 'II' || p === 'III')) {
                ok = "Yes (Check IMDG)"; mark = "LQ Diamond";
            }
        }
        return { ok: ok, mark: mark };
    },

    // 10. LQ Matrix Builder
    "lq-matrix-builder-01": function(v) {
        var ml = parseFloat(v.inner_ml);
        var qty = parseFloat(v.qty);
        var rho = parseFloat(v.rho);
        var tare = parseFloat(v.tare);
        
        var net_l = (ml * qty) / 1000;
        var gross = (net_l * rho) + tare;
        
        // Re-use logic from checker roughly
        var elig = "See Checker";
        if (gross > 30) elig = "Exceeds 30kg Cap!";
        else elig = "Likely OK (Check specifics)";

        return {
            net_l: net_l.toFixed(2),
            gross: gross.toFixed(1),
            elig: elig
        };
    },

    // 11. Outer Count
    "outer-count-calculator": function(v) {
        var t = parseFloat(v.total_l);
        var i = parseFloat(v.inner_l);
        var p = parseFloat(v.per_outer);
        var outers = Math.ceil((t / i) / p);
        return { outers: outers };
    },

    // 12. Carrier Acceptance Note
    "carrier-acceptance-note": function(v) {
        return {
            line: v.carrier + " (" + v.route + "): " + v.unpsn + " => " + v.status + ". Contact: " + v.contact
        };
    },

    // 13. Audit Sheet
    "audit-sheet-builder": function(v) {
        return {
            summary: "Audit: SDS=" + v.sds + ", Class=" + v.class + ", PG=" + v.pg + ", LQ=" + v.lq + ", Docs=" + v.docs
        };
    },

    // 14. Label Size
    "label-size-checker": function(v) {
        var mm = parseFloat(v.face_mm);
        var dist = parseFloat(v.distance_m);
        var edge = "100x100 mm";
        var note = "Standard";
        
        if (mm > 400 || dist > 3) {
            edge = "150x150 mm"; // Recommendation
            note = "Large package/distance";
        }
        return { edge: edge, note: note };
    },

    // --- PHASE 3: CIJ TOOLS ---

    // 15. CIJ Breakpoint
    "cij-print-quality-checklist-breakpoint-explainer-01": function(v) {
        var visc = parseFloat(v.visc);
        var mod = parseFloat(v.mod);
        var risk = "Low";
        var tip = "Optimal param window";
        
        if (visc < 3.5 || visc > 5.5) {
            risk = "High (Viscosity)";
            tip = "Correct viscosity first";
        } else if (mod < 20 || mod > 80) {
            risk = "Medium (Modulation)";
            tip = "Adjust modulation voltage";
        }
        return { risk: risk, tip: tip };
    },

    // 16. CIJ Adhesion
    "cij-print-quality-checklist-adhesion-checker-02": function(v) {
        var sub = v.substrate;
        var surf = v.surface;
        var fam = v.inkfam;
        
        var risk = "Low";
        var action = "Proceed";
        
        if (surf !== 'Dry') {
            risk = "High (Surface State)";
            action = "Clean/Dry or use Acetone";
        } else if (sub === 'PE' || sub === 'OPP film') {
            risk = "Medium (Low Surface Energy)";
            action = "Check Dyne level / Flame treat";
        } else if (sub === 'Glass' && surf === 'Condensation') {
            risk = "Critical";
            action = "Air knifes required";
        }
        
        return { risk: risk, action: action };
    },

    // --- PHASE 4: INK SHELF LIFE TOOLS (17) ---

    // 1. Storage Temp Risk
    "cij-ink-shelf-life-storage-temp-risk-1": function(v) {
        var avg = parseFloat(v.avg_t);
        var min = parseFloat(v.oem_min);
        var max = parseFloat(v.oem_max);
        var type = v.ink_type;
        
        var diff = 0;
        if (avg < min) diff = min - avg;
        if (avg > max) diff = avg - max;
        
        var risk = "OK";
        if (diff > 0) risk = "CAUTION";
        if (diff > 3) risk = "HIGH";
        
        if (type === "UV-curable" && risk === "CAUTION") risk = "HIGH";
        
        return { risk: risk };
    },

    // 2. FIFO & Acc
    "cij-ink-shelf-life-storage-fifo-2": function(v) {
        var mfg = v.mfg_date; // YYYY-MM
        var w = parseFloat(v.warranty_mo);
        // Simple string handling for date
        var parts = mfg.split("-");
        var y = parseInt(parts[0]);
        var m = parseInt(parts[1]);
        
        m += w;
        while(m > 12) { m -= 12; y++; }
        
        var use_by = y + "-" + (m < 10 ? "0"+m : m);
        
        // Warmup parsing "20 / 30" maybe? Or formatted string
        // Actually logic says "If ΔT ≥ 10...". Input is string? No, let's assume user enters "10 / 25" style or just checks delta.
        // Wait, definition said input type string "Move from / to". 
        // Let's rely on simple heuristic or just fixed text if complex.
        // "Explain: Allow several hours if ΔT is big"
        // Let's return the explanation directly.
        
        return { use_by: use_by, warmup_tip: "Plan ≥3h if ΔT ≥ 10°C" };
    },

    // 3. RH Impact
    "cij-ink-shelf-life-storage-rh-impact-3": function(v) {
        var rh = parseFloat(v.rh);
        var fam = v.ink_family;
        
        var dry = 1.0;
        var decap = 1.0;
        
        if (fam.indexOf("TIJ") > -1) {
            // Linear approx 35->0.8, 75->1.4
            dry = 0.8 + (rh - 35) * (0.6 / 40);
            if (rh < 40) decap = 2.0; // Sensitive
        }
        
        return { dry_factor: dry.toFixed(2) + "x", decap_factor: decap.toFixed(2) + "x" };
    },

    // 4. UV Risk
    "cij-ink-shelf-life-storage-uv-risk-4": function(v) {
        var lux = parseFloat(v.lux);
        var t = parseFloat(v.exposure_min);
        var pkg = v.packaging;
        
        var score = (lux * t) / 1000;
        if (pkg.indexOf("Opaque") > -1) score *= 0.4;
        if (pkg.indexOf("Black") > -1) score *= 0.6;
        if (pkg.indexOf("Clear") > -1) score *= 1.2;
        
        var final = Math.min(100, Math.ceil(score));
        return { uv_score: final + "/100" };
    },

    // 5. Orientation
    "cij-ink-shelf-life-storage-orientation-5": function(v) {
        var cart = v.cartridge;
        var white = v.pigment;
        var tip = "Upright (Septum Up)";
        if (white.indexOf("White") > -1) tip += " + Weekly Roll";
        return { tip: tip };
    },

    // 6. Agitation
    "cij-ink-shelf-life-storage-agitation-6": function(v) {
        var b = parseFloat(v.bottles);
        var d = parseFloat(v.days);
        var perDay = Math.ceil(b / d);
        return { schedule: perDay + " bottles/day", signoff: d + " slots" };
    },

    // 7. Hygiene
    "cij-ink-shelf-life-storage-hygiene-7": function(v) {
        return { tasks: "1. Clean Cap | 2. Lint-free Wipe | 3. No Sticks | 4. Waste Bin | 5. Gloves" };
    },

    // 8. AQL
    "cij-ink-shelf-life-storage-aql-8": function(v) {
        var lot = parseFloat(v.lot);
        // Simple lookup simulation
        var n = 10;
        var c = 0;
        if (lot > 1000) n = 80;
        else if (lot > 100) n = 20;
        
        // AQL logic simplified
        var aql = parseFloat(v.aql);
        c = Math.floor(n * aql / 100); 
        
        return { n: n, c: c + " defects" };
    },

    // 9. Viscosity Drift
    "cij-ink-shelf-life-storage-viscosity-9": function(v) {
        var base = parseFloat(v.base_visc);
        var loss = parseFloat(v.solvent_loss);
        var dt = Math.abs(parseFloat(v.delta_t));
        
        var vNew = base * (1 + (loss/100)*2) + (dt * 0.1);
        return { visc: vNew.toFixed(2) };
    },

    // 10. Evap
    "cij-ink-shelf-life-storage-evap-10": function(v) {
        var h = parseFloat(v.run_hours);
        var l = parseFloat(v.makeup_l);
        var t = parseFloat(v.avg_t);
        
        var rate = l / h;
        if (t > 25) rate *= 1.2;
        
        return { evap_index: rate.toFixed(4) + " L/h" };
    },

    // 11. Fireload
    "cij-ink-shelf-life-storage-fireload-11": function(v) {
        var meq = parseFloat(v.meq_l);
        var cap = parseFloat(v.cabinet_cap);
        var rcap = parseFloat(v.room_cap);
        
        var s = "OK";
        if (meq > cap) s = "Exceeds Cabinet!";
        if (meq > rcap) s = "Exceeds Room!";
        
        return { status: s };
    },

    // 12. Decap
    "cij-ink-shelf-life-storage-decap-12": function(v) {
        var fam = v.ink_family;
        var rh = parseFloat(v.rh);
        var base = 30; // min
        
        if (fam.indexOf("aqueous") > -1) base = 15;
        if (rh < 40) base *= 0.5;
        
        return { idle_window: Math.floor(base) + " min" };
    },

    // 13. Q10 Shelf Life
    "cij-ink-shelf-life-storage-q10-13": function(v) {
        var sl = parseFloat(v.shelf_months);
        var tr = parseFloat(v.t_ref);
        var ta = parseFloat(v.t_actual);
        var q = parseFloat(v.q10);
        
        var dt = (ta - tr) / 10;
        var factor = Math.pow(q, dt);
        var adj = sl / factor;
        
        return { adj_months: adj.toFixed(1) + " mo" };
    },

    // 14. Logistics
    "cij-ink-shelf-life-storage-logistics-14": function(v) {
        var r = v.region;
        var c = "Insulated";
        var w = "3h";
        if (r.indexOf("Tropical") > -1) { c="Reefer"; w="6h"; }
        return { controls: c, warmup: w };
    },

    // 15. ROI
    "cij-ink-shelf-life-storage-roi-15": function(v) {
        var clogs = parseFloat(v.clogs);
        var labor = parseFloat(v.labor);
        var scrap = parseFloat(v.ink_scrap);
        // Cost assumptions: 1 clog = 1h labor?
        var cost = (clogs * labor) + (scrap * 100); // 100/L assumed
        return { savings: "$" + cost.toFixed(0) };
    },
    
    // 16. FIFO Monitor
    "cij-ink-shelf-life-storage-fifomonitor-16": function(v) {
        // v.lots string "202301, 202305, 202212"
        var flag = "Pass";
        // logic placeholder
        if (v.lots.indexOf("2024") > -1 && v.lots.indexOf("2023") > -1) flag = "Check Sort";
        return { flag: flag };
    },
    
    // 17. Calendar
    "cij-ink-shelf-life-storage-calendar-17": function(v) {
        return { checklist: "Jan: Freeze | Jul: Heat | Oct: RH High" };
    }

});

// --- v13 Engine (Reactive) ---
// Listen for Input Changes (Auto-Calc)
document.addEventListener('input', function(e) {
    var container = e.target.closest('[data-itb-calculator]');
    if (container) {
        window.ozExecuteCalc(container);
    }
});

// Initial boot
var calcs = document.querySelectorAll('[data-itb-calculator]');
calcs.forEach(function(c) { window.ozExecuteCalc(c); });

console.log('OZ: v5.1 Reactive Engine Fully Loaded');
"""

# Check for Smart Quotes
if "’" in js_logic or "“" in js_logic or "”" in js_logic:
    print("FATAL ERROR: Smart quotes detected in JS logic!")
    exit()

# Hex Encode
hex_payload = binascii.hexlify(js_logic.encode('utf-8')).decode('utf-8')

# Final Verification
print(f"Payload Length: {len(hex_payload)}")
print(f"Sample: {hex_payload[:50]}...")

# Injection Logic
# Level 5 Loader: Timeout Decoupled
loader_script_v13_reactive = """<script>!function(){if(!window.ozExecuteCalc)window.ozExecuteCalc=function(){console.warn("OZ: Loading...")};function l(){setTimeout(function(){var e=document.getElementById("oz-safe-code");if(e){var v=e.value;if(v&&v.length%2===0){var s="";for(var i=0;i<v.length;i+=2)s+=String.fromCharCode(parseInt(v.substr(i,2),16));window.eval(s)}}}, 500)}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",l);else l();}();</script>"""

loader_html = f"""<!-- OZ Calc v13.0 Reactive (Auto-Calc) -->
<div class="oz-calculator-app" style="font-size:0;line-height:0;margin:0;padding:0;display:inline;">
<input type="hidden" id="oz-safe-code" value="{hex_payload}">
{loader_script_v13_reactive}
<style>.oz-calculator-app {{ margin:0; padding:0; font-size:0; line-height:0; }}.itb-outputs {{ display: block; margin-top: 20px; padding: 15px; background: #f0fdf4; border: 1px solid #16a34a; border-radius: 6px; font-size: 16px; line-height: 1.5; }}.itb-output-group {{ margin-bottom: 8px; display: flex; justify-content: space-between; border-bottom: 1px dashed #bbf7d0; padding-bottom: 4px; }}.itb-output-group:last-child {{ border-bottom: none; }}</style>
</div>"""

loader_html = re.sub(r'\n', '', loader_html)

# Read original
with open('errorpost.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Strip existing loader blocks (Aggressive)
# We look for the marker, or just the bottom section
if '<!-- OZ Calc' in content:
    content = content.split('<!-- OZ Calc')[0]

# Strip existing loader blocks (Aggressive)
# We look for the marker, or just the bottom section
if '<!-- OZ Calc' in content:
    content = content.split('<!-- OZ Calc')[0]

# Hide Buttons (Don't delete, just hide)
# This appeases WP auto-formatters that might try to "fix" a missing button
content = re.sub(r'<button', r'<button style="display:none !important;"', content)

# Strip any trailing newlines
content = content.rstrip()

# Inject
final_content = content + "\n" + loader_html

with open('errorpost.html', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("INJECTION COMPLETE: Updated errorpost.html with v5 Payload (data-var support).")
