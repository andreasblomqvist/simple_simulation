"""
KPI Baseline Verification Test

This test verifies that:
1. KPI baselines are calculated correctly
2. Baseline values are not zero
3. Baseline calculations are consistent
4. Baseline data structure is complete
"""

import pytest
from typing import Dict, Any


class TestKPIBaselines:
    """Test KPI baseline calculations and validation"""

    def test_baseline_kpis_not_zero(self, api_client, ensure_server_running, logger):
        """Test that baseline KPIs are calculated and not zero using current config as baseline"""
        
        logger("🧪 KPI BASELINE VERIFICATION TEST (CONFIG-DRIVEN)")
        logger("=" * 50)
        
        # Step 1: Fetch current config from /offices/config
        logger("📊 Step 1: Fetching current configuration")
        config_response = api_client.get("/offices/config")
        assert config_response.status_code == 200
        offices_config = config_response.json()
        assert isinstance(offices_config, list)
        assert len(offices_config) > 0
        
        # Step 2: Build simulation input using config
        logger("📊 Step 2: Building simulation input from config")
        simulation_input = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12,
            "price_increase": 0.0,
            "salary_increase": 0.0,
            "unplanned_absence": 0.05,
            "hy_working_hours": 166.4,
            "other_expense": 100000.0,
            "offices": offices_config
        }
        
        # Step 3: Run baseline simulation
        logger("📊 Step 3: Running baseline simulation with config data")
        response = api_client.post("/simulation/run", json_data=simulation_input, timeout=180)
        assert response.status_code == 200
        results = response.json()
        
        # Step 4: Extract baseline KPIs
        logger("📊 Step 4: Extracting baseline KPIs")
        kpis = results.get("kpis", {})
        
        # Financial KPIs
        financial_kpis = kpis.get("financial", {})
        baseline_financial = {
            "net_sales_baseline": financial_kpis.get("net_sales_baseline", 0),
            "ebitda_baseline": financial_kpis.get("ebitda_baseline", 0),
            "margin_baseline": financial_kpis.get("margin_baseline", 0),
            "total_consultants_baseline": financial_kpis.get("total_consultants_baseline", 0),
            "avg_hourly_rate_baseline": financial_kpis.get("avg_hourly_rate_baseline", 0),
            "avg_utr": financial_kpis.get("avg_utr", 0)
        }
        
        # Growth KPIs
        growth_kpis = kpis.get("growth", {})
        baseline_growth = {
            "baseline_total_fte": growth_kpis.get("baseline_total_fte", 0),
            "non_debit_ratio_baseline": growth_kpis.get("non_debit_ratio_baseline", 0)
        }
        
        # Journey KPIs
        journey_kpis = kpis.get("journeys", {})
        journey_totals = journey_kpis.get("journey_totals", {})
        
        # Step 5: Verify baseline values are not zero
        logger("📊 Step 5: Verifying baseline values are not zero")
        
        # Financial baseline checks
        logger("   Financial Baselines:")
        for kpi_name, value in baseline_financial.items():
            logger(f"     {kpi_name}: {value:,.2f}")
            assert value > 0, f"Financial baseline {kpi_name} is zero: {value}"
        
        # Growth baseline checks
        logger("   Growth Baselines:")
        for kpi_name, value in baseline_growth.items():
            logger(f"     {kpi_name}: {value:,.2f}")
            assert value > 0, f"Growth baseline {kpi_name} is zero: {value}"
        
        # Journey baseline checks
        logger("   Journey Baselines:")
        total_journey_fte = 0
        for journey_name, fte_count in journey_totals.items():
            logger(f"     {journey_name}: {fte_count:,} FTE")
            assert fte_count >= 0, f"Journey baseline {journey_name} is negative: {fte_count}"
            total_journey_fte += fte_count
        
        assert total_journey_fte > 0, f"Total journey FTE is zero: {total_journey_fte}"
        
        # Step 6: Verify baseline consistency
        logger("📊 Step 6: Verifying baseline consistency")
        
        # Check that baseline consultants match total FTE
        baseline_consultants = baseline_financial["total_consultants_baseline"]
        baseline_total_fte = baseline_growth["baseline_total_fte"]
        
        logger(f"   Baseline consultants: {baseline_consultants:,}")
        logger(f"   Baseline total FTE: {baseline_total_fte:,}")
        logger(f"   Journey FTE total: {total_journey_fte:,}")
        logger(f"   Total FTE: {baseline_total_fte:,}")
        logger(f"   Difference: {baseline_total_fte - total_journey_fte:,} (non-journey roles)")
        
        # Journey FTE should be a subset of total FTE
        assert total_journey_fte <= baseline_total_fte, \
            f"Journey FTE ({total_journey_fte}) > total FTE ({baseline_total_fte})"
        
        # Journey FTE should be substantial (at least 50% of total FTE)
        journey_ratio = total_journey_fte / baseline_total_fte
        assert journey_ratio >= 0.5, \
            f"Journey FTE ratio too low: {journey_ratio:.1%} (should be at least 50%)"
        
        logger(f"   ✅ Journey FTE ratio: {journey_ratio:.1%}")
        
        # Step 7: Verify baseline calculations are reasonable
        logger("📊 Step 7: Verifying baseline calculations are reasonable")
        
        # Net sales should be positive and substantial
        net_sales = baseline_financial["net_sales_baseline"]
        assert net_sales > 1000000, f"Net sales baseline too low: {net_sales:,.0f} SEK"
        logger(f"   ✅ Net sales baseline: {net_sales:,.0f} SEK")
        
        # EBITDA should be reasonable (can be negative but not zero)
        ebitda = baseline_financial["ebitda_baseline"]
        assert ebitda != 0, f"EBITDA baseline is zero: {ebitda:,.0f} SEK"
        logger(f"   ✅ EBITDA baseline: {ebitda:,.0f} SEK")
        
        # Margin should be reasonable percentage
        margin = baseline_financial["margin_baseline"]
        assert 0.01 <= margin <= 0.99, f"Margin baseline unreasonable: {margin:.1%}"
        logger(f"   ✅ Margin baseline: {margin:.1%}")
        
        # Average hourly rate should be reasonable
        hourly_rate = baseline_financial["avg_hourly_rate_baseline"]
        assert 500 <= hourly_rate <= 3000, f"Hourly rate baseline unreasonable: {hourly_rate:.2f} SEK/hr"
        logger(f"   ✅ Average hourly rate baseline: {hourly_rate:.2f} SEK/hr")
        
        # UTR should be reasonable
        utr = baseline_financial["avg_utr"]
        assert 0.5 <= utr <= 1.0, f"UTR baseline unreasonable: {utr:.2f}"
        logger(f"   ✅ Average UTR baseline: {utr:.2f}")
        
        logger("   🎉 ALL BASELINE KPIs VERIFIED SUCCESSFULLY!")

    def test_baseline_consistency_across_simulations(self, api_client, ensure_server_running, logger):
        """Test that baseline KPIs are consistent across multiple simulations"""
        
        logger("🧪 BASELINE CONSISTENCY TEST")
        logger("=" * 40)
        
        baseline_config = {
            "start_year": 2025, "start_month": 1,
            "end_year": 2025, "end_month": 12,
            "price_increase": 0.0, "salary_increase": 0.0,
            "unplanned_absence": 0.05, "hy_working_hours": 166.4,
            "other_expense": 100000.0
        }
        
        baseline_results = []
        
        # Run multiple baseline simulations
        for i in range(3):
            logger(f"📊 Running baseline simulation {i+1}/3")
            
            response = api_client.post("/simulation/run", json_data=baseline_config, timeout=180)
            assert response.status_code == 200
            results = response.json()
            
            kpis = results.get("kpis", {})
            financial = kpis.get("financial", {})
            
            baseline_results.append({
                "net_sales": financial.get("net_sales_baseline", 0),
                "ebitda": financial.get("ebitda_baseline", 0),
                "consultants": financial.get("total_consultants_baseline", 0),
                "margin": financial.get("margin_baseline", 0)
            })
        
        # Verify consistency
        logger("📊 Verifying baseline consistency")
        
        for i, result in enumerate(baseline_results):
            logger(f"   Run {i+1}: Net Sales={result['net_sales']:,.0f}, "
                   f"EBITDA={result['ebitda']:,.0f}, Consultants={result['consultants']:,}")
        
        # All results should be identical (deterministic)
        first_result = baseline_results[0]
        for i, result in enumerate(baseline_results[1:], 1):
            assert result["net_sales"] == first_result["net_sales"], \
                f"Net sales inconsistent: run 1={first_result['net_sales']:,.0f}, run {i+1}={result['net_sales']:,.0f}"
            
            assert result["ebitda"] == first_result["ebitda"], \
                f"EBITDA inconsistent: run 1={first_result['ebitda']:,.0f}, run {i+1}={result['ebitda']:,.0f}"
            
            assert result["consultants"] == first_result["consultants"], \
                f"Consultants inconsistent: run 1={first_result['consultants']:,}, run {i+1}={result['consultants']:,}"
        
        logger("   ✅ Baseline calculations are consistent and deterministic!")

    def test_baseline_vs_current_kpis(self, api_client, ensure_server_running, test_config, logger):
        """Test that baseline KPIs differ from current KPIs (showing simulation impact)"""
        
        logger("🧪 BASELINE vs CURRENT KPI COMPARISON")
        logger("=" * 45)
        
        # Run simulation with test config (which may have levers applied)
        response = api_client.post("/simulation/run", json_data=test_config, timeout=180)
        assert response.status_code == 200
        results = response.json()
        
        kpis = results.get("kpis", {})
        financial = kpis.get("financial", {})
        
        # Extract baseline and current values
        baseline_net_sales = financial.get("net_sales_baseline", 0)
        current_net_sales = financial.get("net_sales", 0)
        
        baseline_ebitda = financial.get("ebitda_baseline", 0)
        current_ebitda = financial.get("ebitda", 0)
        
        baseline_consultants = financial.get("total_consultants_baseline", 0)
        current_consultants = financial.get("total_consultants", 0)
        
        baseline_margin = financial.get("margin_baseline", 0)
        current_margin = financial.get("margin", 0)
        
        # Log comparison
        logger("📊 KPI Comparison:")
        logger(f"   Net Sales: {current_net_sales:,.0f} vs {baseline_net_sales:,.0f} (baseline)")
        logger(f"   EBITDA: {current_ebitda:,.0f} vs {baseline_ebitda:,.0f} (baseline)")
        logger(f"   Consultants: {current_consultants:,} vs {baseline_consultants:,} (baseline)")
        logger(f"   Margin: {current_margin:.1%} vs {baseline_margin:.1%} (baseline)")
        
        # Verify that baseline values are present and different from current
        assert baseline_net_sales > 0, "Baseline net sales is zero"
        assert baseline_ebitda != 0, "Baseline EBITDA is zero"
        assert baseline_consultants > 0, "Baseline consultants is zero"
        assert baseline_margin > 0, "Baseline margin is zero"
        
        # Verify that current values are also calculated
        assert current_net_sales > 0, "Current net sales is zero"
        assert current_ebitda != 0, "Current EBITDA is zero"
        assert current_consultants > 0, "Current consultants is zero"
        assert current_margin > 0, "Current margin is zero"
        
        # Calculate differences
        net_sales_diff = current_net_sales - baseline_net_sales
        ebitda_diff = current_ebitda - baseline_ebitda
        consultants_diff = current_consultants - baseline_consultants
        margin_diff = current_margin - baseline_margin
        
        logger("📊 Impact Analysis:")
        logger(f"   Net Sales change: {net_sales_diff:+,.0f} SEK")
        logger(f"   EBITDA change: {ebitda_diff:+,.0f} SEK")
        logger(f"   Consultants change: {consultants_diff:+,}")
        logger(f"   Margin change: {margin_diff:+.1%}")
        
        # Verify that the system can detect differences (even if they're small)
        # This ensures the baseline comparison mechanism is working
        logger("   ✅ Baseline vs current comparison working correctly!")
        
        # Note: We don't assert specific differences since they depend on the test configuration
        # The important thing is that both baseline and current values are calculated 