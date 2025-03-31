import pytest

from bfcl.runners import PlainJsonRunner


class TestPlainJsonRunner:
    """Test the PlainJsonRunner class."""

    @pytest.fixture
    def runner(self):
        """Return a fixture for the PlainJsonRunner instance."""
        return PlainJsonRunner()

    def test_positive_irrelevance(self, runner):
        """Test the positive irrelevance sample."""
        sample = {
            "id": "live_irrelevance_9-0-9",
            "completion": "I'm sorry, I don't understand. Can you please rephrase your question?",
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_irrelevance(self, runner):
        """Test the negative irrelevance sample."""
        sample = {
            "id": "live_irrelevance_9-0-9",
            "completion": '[{"test_name": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_positive_relevance(self, runner):
        """Test the positive relevance sample."""
        sample = {
            "id": "live_relevance_15-15-0",
            "completion": '[{"test_name": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_relevance(self, runner):
        """Test the negative relevance sample."""
        sample = {
            "id": "live_relevance_15-15-0",
            "completion": "I'm sorry, I don't understand. Can you please rephrase your question?",
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_positive_ast_simple_with_optional_parameter(self, runner):
        """Test the positive ast simple sample with optional parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5, "z": 0}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_ast_simple_without_optional_parameter(self, runner):
        """Test the positive ast simple sample without optional parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_ast_simple_value_error(self, runner):
        """Test the negative ast simple sample with value error."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 5, "y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("value_error")

    def test_negative_ast_simple_type_error(self, runner):
        """Test the negative ast simple sample with type error."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": [5], "y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("type_error")

    def test_negative_ast_simple_missing_required_parameter(self, runner):
        """Test the negative ast simple sample with missing required parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_ast_simple_unexpected_parameter(self, runner):
        """Test the negative ast simple sample with unexpected parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5, "w": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("unexpected_param")

    def test_negative_ast_simple_invalid_json_format(self, runner):
        """Test the negative ast simple sample with invalid JSON format."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot":, {"x": 4, "y": 5, "w": 1}}]'}
        result = runner.run(**sample)
        assert result.get("formatted") is False

    def test_positive_ast_multiple_with_optional_parameter(self, runner):
        """Test the positive ast multiple sample with optional parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2], "rounding": 0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_ast_multiple_without_optional_parameter(self, runner):
        """Test the positive ast multiple sample without optional parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2]}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_ast_multiple_missing_required_parameter(self, runner):
        """Test the negative ast multiple sample with missing required parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "rounding": 0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_ast_multiple_unexpected_parameter(self, runner):
        """Test the negative ast multiple sample with unexpected parameter."""
        sample = {
            "id": "multiple_3",
            "completion": (
                '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2], "rounding": 0, '
                '"unexpected_param": 1}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("unexpected_param")

    def test_positive_parallel_with_optional_parameter(self, runner):
        """Test the positive parallel sample with optional parameter."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin", "model_3d": true}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_parallel_without_optional_parameter(self, runner):
        """Test the positive parallel sample without optional parameter."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c"}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin"}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_parallel_different_order(self, runner):
        """Test the positive parallel sample with different order."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin"}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c"}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_parallel_less_functions(self, runner):
        """Test the negative parallel sample with less functions than possible answers."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin", "model_3d": true}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_parallel_more_functions(self, runner):
        """Test the negative parallel sample with more functions than possible answers."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin", "model_3d": true}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_parallel_unexpected_parameter(self, runner):
        """Test the negative parallel sample with unexpected parameter."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "normal hemoglobin", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": '
                '{"protein_name": "rat hemoglobin", "model_3d": true, "wrong_param": 1}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith(
            "cannot_find_match"
        )

    def test_negative_parallel_missing_required_parameter(self, runner):
        """Test the negative parallel sample with missing required parameter."""
        sample = {
            "id": "parallel_3",
            "completion": (
                '[{"protein_info.get_sequence_and_3D": {"protein_name": "HbA1c", "model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"model_3d": true}}, '
                '{"protein_info.get_sequence_and_3D": {"protein_name": "rat hemoglobin", "model_3d": true}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith(
            "cannot_find_match"
        )

    def test_positive_parallel_multiple(self, runner):
        """Test the positive parallel multiple sample."""
        sample = {
            "id": "parallel_multiple_1",
            "completion": (
                '[{"area_rectangle.calculate": {"length": 7.0, "breadth": 3.0}}, '
                '{"area_circle.calculate": {"radius": 5.0}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_parallel_multiple_less_functions(self, runner):
        """Test the negative parallel multiple sample with less function calls than possible answers."""
        sample = {
            "id": "parallel_multiple_1",
            "completion": '[{"area_rectangle.calculate": {"length": 7.0, "breadth": 3.0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_parallel_multiple_more_functions(self, runner):
        """Test the negative parallel multiple sample with more function calls than possible answers."""
        sample = {
            "id": "parallel_multiple_1",
            "completion": (
                '[{"area_rectangle.calculate": {"length": 7.0, "breadth": 3.0}}, '
                '{"area_circle.calculate": {"radius": 5.0}}, '
                '{"area_circle.calculate": {"radius": 5.0}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_parallel_multiple_unexpected_parameter(self, runner):
        """Test the negative parallel multiple sample with unexpected parameter."""
        sample = {
            "id": "parallel_multiple_1",
            "completion": (
                '[{"area_rectangle.calculate": {"length": 7.0, "breadth": 3.0, "wrong_param": 1}}, '
                '{"area_circle.calculate": {"radius": 5.0}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith(
            "cannot_find_match"
        )

    def test_negative_parallel_multiple_missing_required_parameter(self, runner):
        """Test the negative parallel multiple sample with missing required parameter."""
        sample = {
            "id": "parallel_multiple_1",
            "completion": '[{"area_rectangle.calculate": {"length": 7.0}}, {"area_circle.calculate": {"radius": 5.0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith(
            "cannot_find_match"
        )

    def test_positive_java(self, runner):
        """Test the positive java sample."""
        sample = {
            "id": "java_2",
            "completion": (
                '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "dbMonitor", "view": "EmployeeView", '
                '"source": "SELECT * FROM Employee WHERE status = \'active\'"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_java_wrong_function_name(self, runner):
        """Test the negative java sample with wrong function name."""
        sample = {
            "id": "java_2",
            "completion": (
                '[{"FireBirdUtils.WrongFunctionName": {"monitor": "dbMonitor", "view": "EmployeeView", "source": '
                "\"SELECT * FROM Employee WHERE status = 'active'\"}}]"
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_java_missing_required_parameter(self, runner):
        """Test the negative java sample with missing required parameter."""
        sample = {
            "id": "java_2",
            "completion": (
                '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "dbMonitor", "view": "EmployeeView"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_java_wrong_value(self, runner):
        """Test the negative java sample with wrong value."""
        sample = {
            "id": "java_2",
            "completion": (
                '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "wrongMonitor", "view": "EmployeeView", '
                '"source": "SELECT * FROM Employee WHERE status = \'active\'"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("value_error")

    def test_negative_java_unexpected_parameter(self, runner):
        """Test the negative java sample with unexpected parameter."""
        sample = {
            "id": "java_2",
            "completion": (
                '[{"FireBirdUtils.getViewSourceWithHeader": {"monitor": "dbMonitor", "view": "EmployeeView", "source": '
                '"SELECT * FROM Employee WHERE status = \'active\'", "unexpected_param": "unexpected_value"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("unexpected_param")

    def test_positive_javascript(self, runner):
        """Test the positive javascript sample."""
        sample = {
            "id": "javascript_11",
            "completion": (
                '[{"prioritizeAndSort": {"items": "myItemList", "priorityStatus": "urgent", "ascending": "true"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_javascript_wrong_function_name(self, runner):
        """Test the negative javascript sample with wrong function name."""
        sample = {
            "id": "javascript_11",
            "completion": (
                '[{"WrongFunctionName": {"items": "myItemList", "priorityStatus": "urgent", "ascending": "true"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_negative_javascript_missing_required_parameter(self, runner):
        """Test the negative javascript sample with missing required parameter."""
        sample = {
            "id": "javascript_11",
            "completion": '[{"prioritizeAndSort": {"items": "myItemList", "priorityStatus": "urgent"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_javascript_wrong_value(self, runner):
        """Test the negative javascript sample with wrong value."""
        sample = {
            "id": "javascript_11",
            "completion": (
                '[{"prioritizeAndSort": {"items": "myItemList", "priorityStatus": "urgent", "ascending": "false"}}]'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("value_error")

    def test_positive_rest(self, runner):
        """Test the positive REST sample."""
        sample = {
            "id": "rest_49",
            "completion": (
                'requests.get("https://api.open-meteo.com/v1/forecast", '
                'params={"latitude": "39.113014", "longitude": "-105.358887", '
                '"daily": "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum",'
                '"temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "forecast_days": 10, "timezone": "auto"})'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_rest_execution_failure(self, runner):
        """Test the negative REST sample with execution failure."""
        sample = {
            "id": "rest_49",
            "completion": (
                'requests.get.("https://api.open-meteo.com/v1/forecast",'
                'params={"latitude": "39.113014", "longitude": "-105.358887", '
                'daily": "temperature_2m_max,precipitation_sum", "temperature_unit": "fahrenheit", '
                'wind_speed_unit": "mph", "forecast_days": 10, "timezone": "auto"})'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("execution_error")

    def test_negative_rest_status_code_error(self, runner):
        """Test the negative REST sample with status code error."""
        sample = {
            "id": "rest_49",
            "completion": (
                'requests.get("https://api.open-meteo.com/v1/forecast", '
                'params={"latitude": "39.113014", '
                '"daily": "temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum",'
                '"temperature_unit": "fahrenheit", "wind_speed_unit": "mph", '
                '"forecast_days": 10, "timezone": "auto"})'
            ),
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith(
            "wrong_status_code"
        )

    def test_positive_exec_simple_exact_match(self, runner):
        """Test the positive exec simple sample with exact match."""
        sample = {"id": "exec_simple_1", "completion": "calc_binomial_probability(n=30, k=15, p=0.5)"}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_exec_simple_structural_match(self, runner):
        """Test the positive exec simple sample with structural match."""
        sample = {"id": "exec_simple_58", "completion": "get_weather_data(coordinates=[90.00, 0.00])"}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_exec_simple_real_time_match(self, runner):
        """Test the positive exec simple sample with real_time_match."""
        sample = {"id": "exec_simple_54", "completion": "get_stock_price_by_stock_name(stock_name='AAPL')"}
        result = runner.run(**sample)
        assert result.get("correct") is True
