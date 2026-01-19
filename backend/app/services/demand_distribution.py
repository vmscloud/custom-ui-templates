"""
Demand Distribution 서비스

Demand Distribution 비즈니스 로직 처리
"""

from app.repositories.demand_distribution import DemandDistributionRepository


class DemandDistributionService:
    """Demand Distribution 비즈니스 로직"""

    # 기본 헤더 (고정 컬럼)
    FIXED_HEADERS = [
        {"columnName": "cust_id", "displayText": "text-cust_id", "category": "fixed"},
        {"columnName": "item_group_id", "displayText": "text-item_group_id", "category": "fixed"},
        {"columnName": "prod_type", "displayText": "text-prod_type", "category": "fixed"},
        {"columnName": "item_size_type", "displayText": "text-item_size_type", "category": "fixed"},
    ]

    def __init__(self):
        self.repository = DemandDistributionRepository()

    def get_demand_versions(self, project_id: str) -> dict:
        """
        Demand Version 목록 조회

        Args:
            project_id: 프로젝트 ID

        Returns:
            조회 결과 딕셔너리
        """
        results = self.repository.get_demand_versions(project_id)

        if results:
            return {
                "success": True,
                "count": len(results),
                "data": results,
            }
        else:
            return {
                "success": True,
                "count": 0,
                "data": [],
                "message": "NO_CONTENT",
            }

    def get_demand_distribution(
        self,
        project_id: str,
        demand_ver: str,
        aggregate_type: str = "month",
        summary: str = "sum",
        uom_type: str = "QTY",
        columns: list[str] | None = None,
    ) -> dict:
        """
        Demand Distribution 데이터 조회

        Args:
            project_id: 프로젝트 ID
            demand_ver: Demand Version
            aggregate_type: 집계 타입 (day/week/month)
            summary: 집계 방식 (sum/count)
            uom_type: UOM 타입
            columns: 표시할 컬럼 목록

        Returns:
            조회 결과 딕셔너리 (data, headers 포함)
        """
        if columns is None:
            columns = []

        # 기본 데이터 조회
        results = self.repository.get_demand_distribution(
            project_id=project_id,
            demand_ver=demand_ver,
            aggregate_type=aggregate_type,
            summary=summary,
            uom_type=uom_type,
        )

        # 헤더 생성
        headers = self._build_headers(project_id, uom_type)

        # Total 데이터 추가
        if results:
            results = self._add_total_data(results, headers, summary)

        if results:
            return {
                "success": True,
                "count": len(results),
                "data": results,
                "headers": headers,
            }
        else:
            return {
                "success": True,
                "count": 0,
                "data": [],
                "headers": headers,
                "message": "NO_CONTENT",
            }

    def get_demand_distribution_columns(self, project_id: str) -> dict:
        """
        Demand Distribution 컬럼 메타데이터 조회

        Args:
            project_id: 프로젝트 ID

        Returns:
            컬럼 메타데이터
        """
        # 고정 컬럼
        columns = [
            {"columnName": "cust_id", "displayText": "Customer", "category": "fixed"},
            {"columnName": "item_group_id", "displayText": "Item Group", "category": "fixed"},
            {"columnName": "prod_type", "displayText": "Prod Type", "category": "fixed"},
            {"columnName": "item_size_type", "displayText": "Item Size Type", "category": "fixed"},
        ]

        # 동적 컬럼 (속성)
        prop_columns = self.repository.get_demand_distribution_columns(project_id)
        for col in prop_columns:
            columns.append({
                "columnName": f"prop_{col['prop_id'].lower()}",
                "displayText": col["display_text"],
                "category": "dynamic",
            })

        return {
            "success": True,
            "count": len(columns),
            "data": columns,
        }

    def get_uom_preference(
        self,
        project_id: str,
        user_id: str,
        menu_id: str | None = None,
    ) -> dict:
        """
        UOM Type 사용자 설정 조회

        우선순위: user_setting_value > project_setting_value > default_value

        Args:
            project_id: 프로젝트 ID
            user_id: 사용자 ID
            menu_id: 메뉴 ID

        Returns:
            UOM 타입 설정
        """
        result = self.repository.get_uom_preference(project_id, user_id, menu_id)

        if result is None:
            return {
                "success": True,
                "uomType": "QTY",  # 기본값
            }

        # 우선순위에 따라 값 결정
        uom_type = (
            result.get("user_setting_value")
            or result.get("project_setting_value")
            or result.get("default_value")
            or "QTY"
        )

        return {
            "success": True,
            "uomType": uom_type,
        }

    def _build_headers(self, project_id: str, uom_type: str) -> list[dict]:
        """
        응답 헤더 생성

        Args:
            project_id: 프로젝트 ID
            uom_type: UOM 타입

        Returns:
            헤더 목록
        """
        headers = []

        # 고정 헤더 추가
        for h in self.FIXED_HEADERS:
            headers.append({
                **h,
                "category": uom_type,
            })

        return headers

    def _add_total_data(
        self,
        data: list[dict],
        headers: list[dict],
        summary: str,
    ) -> list[dict]:
        """
        Total 행 데이터 추가

        Args:
            data: 원본 데이터
            headers: 헤더 목록
            summary: 집계 방식 (sum/count)

        Returns:
            Total 행이 추가된 데이터
        """
        if not data:
            return data

        # sum 모드일 때만 원본 데이터 유지
        origin_data = list(data) if summary == "sum" else []
        summary_data = []

        # 고유한 due_date 목록
        due_dates = list(set(d.get("due_date") for d in data if d.get("due_date")))

        for header in headers:
            column_name = header["columnName"]

            # 해당 컬럼의 고유 값들
            distinct_values = list(set(
                d.get(column_name) for d in data if d.get(column_name) is not None
            ))

            # due_date별 합계
            for due_date in due_dates:
                filtered = [d for d in data if d.get("due_date") == due_date]
                summary_amount = self._get_summary_amount(filtered, summary)
                summary_data.append({
                    "due_date": due_date,
                    "qty": summary_amount,
                    "total": summary_amount,
                    column_name: "🚀-text-total",
                })

            # 각 값별 전체 합계
            for value in distinct_values:
                filtered = [d for d in data if d.get(column_name) == value]
                summary_amount = self._get_summary_amount(filtered, summary)
                summary_data.append({
                    "due_date": "🚀-text-demand-total",
                    "qty": summary_amount,
                    "total": summary_amount,
                    column_name: value,
                })

            # 전체 합계
            if data:
                total_amount = self._get_summary_amount(data, summary)
                summary_data.append({
                    "due_date": "🚀-text-demand-total",
                    "qty": total_amount,
                    "total": total_amount,
                    column_name: "🚀-text-total",
                })

        return origin_data + summary_data

    def _get_summary_amount(self, data: list[dict], summary: str) -> float:
        """
        집계 값 계산

        Args:
            data: 대상 데이터
            summary: 집계 방식 (sum/count)

        Returns:
            집계 값
        """
        if summary == "sum":
            return sum(d.get("qty", 0) for d in data)
        elif summary == "count":
            return len(set(d.get("item_id") for d in data if d.get("item_id")))
        return 0
