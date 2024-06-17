import itertools
import typing
import uuid

import seal_lambda_invoke
from seal_logging import logger

from . import exceptions, models
from .client import Client
from .settings import Settings


class Service:
    def __init__(
        self,
        settings: Settings,
        client: Client,
    ) -> None:
        self._client = client
        self._settings = settings

    def list_artifacts_for_library(
        self,
        library_escaped_name: str,
        library_package_manager: models.PackageManager,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.List[models.Artifact]:
        results: typing.List[models.Artifact] = []
        offset = 0
        finished = False

        while not finished:
            # read a page
            logger.debug(
                "lib-artifact-server listing versions for library %s %s offset %d",
                library_escaped_name,
                library_package_manager,
                offset,
            )
            results_page = self.list_artifacts(
                library_escaped_name=library_escaped_name,
                library_package_manager=library_package_manager,
                request_context=request_context,
                offset=offset,
            )
            # handle pagination
            offset = results_page.offset + len(results_page.items)
            finished = offset == results_page.total
            # add the results
            results.extend(results_page.items)

        logger.debug(
            "lib-artifact-server listed versions for library %s %s - %d results",
            library_escaped_name,
            library_package_manager,
            len(results),
        )
        return results

    def list_all_artifacts(
        self,
        library_escaped_name: typing.Optional[str] = None,
        library_package_manager: typing.Optional[models.PackageManager] = None,
        file_name: typing.Optional[str] = None,
        library_version_ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.List[models.Artifact]:
        results: typing.List[models.Artifact] = []
        offset = 0
        finished = False

        while not finished:
            results_page = self.list_artifacts(
                library_escaped_name=library_escaped_name,
                library_package_manager=library_package_manager,
                library_version_ids=library_version_ids,
                file_name=file_name,
                request_context=request_context,
                offset=offset,
            )
            # handle pagination
            offset = results_page.offset + len(results_page.items)
            finished = offset == results_page.total
            # add the results
            results.extend(results_page.items)
        return results

    def get_artifact_metadata_by_library_escaped_name(
        self,
        library_escaped_name: str,
        library_package_manager: models.PackageManager,
        file_name: str,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Artifact:
        # read a page
        logger.debug(
            "lib-artifact-server get library version metadata %s %s %s",
            library_escaped_name,
            library_package_manager,
            file_name,
        )
        results_page = self.list_artifacts(
            library_escaped_name=library_escaped_name,
            library_package_manager=library_package_manager,
            file_name=file_name,
            request_context=request_context,
            limit=1,
        )

        if results_page.total > 1:
            raise exceptions.ArtifactManagementMoreThanOnArtifactForFile()
        if results_page.total == 0 or len(results_page.items) == 0:
            raise exceptions.ArtifactNotFound()
        item = results_page.items[0]

        logger.debug(
            "lib-artifact-server got library version metadata %s %s %s %s",
            library_escaped_name,
            library_package_manager,
            file_name,
            item.id,
        )
        return item

    def get_artifact_metadata_by_library_version(
        self,
        library_version_id: uuid.UUID,
        file_name: str,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Artifact:
        # read a page
        logger.debug(
            "lib-artifact-server get library version metadata by library version ID: %s and filename: %s",
            library_version_id,
            file_name,
        )
        results_page = self.list_artifacts(
            library_version_ids=[library_version_id],
            file_name=file_name,
            request_context=request_context,
            limit=1,
        )

        if results_page.total > 1:
            raise exceptions.ArtifactManagementMoreThanOnArtifactForFile()
        if results_page.total == 0 or len(results_page.items) == 0:
            raise exceptions.ArtifactNotFound()
        item = results_page.items[0]

        logger.debug(
            "lib-artifact-server got artifact metadata %s %s %s",
            library_version_id,
            file_name,
            item.id,
        )
        return item

    def list_artifacts(
        self,
        library_escaped_name: typing.Optional[str] = None,
        library_package_manager: typing.Optional[models.PackageManager] = None,
        file_name: typing.Optional[str] = None,
        library_version_ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        offset: int = 0,
        limit: int = 50,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> seal_lambda_invoke.page.LimitOffsetPage[models.Artifact]:
        # Protect against large queries
        query: typing.Dict[str, str] = {}
        if library_escaped_name is not None:
            query["library_escaped_name"] = library_escaped_name
        if library_package_manager is not None:
            query["library_package_manager"] = library_package_manager.value
        if file_name is not None:
            query["file_name"] = file_name

        multi_value_query = {}
        if library_version_ids is not None:
            multi_value_query["library_version_id"] = [
                str(id_) for id_ in library_version_ids
            ]

        results_page: seal_lambda_invoke.page.LimitOffsetPage[
            models.Artifact
        ] = self._client.lambda_service.invoke_paginated_list_http_lambda(
            item_type=models.Artifact,
            function_name=self._settings.artifact_management_lambda_name,
            path="/artifact/",
            query=query,
            multi_value_query=multi_value_query,
            offset=offset,
            limit=limit,
            context=request_context,
        )
        return results_page

    def get_library_version_metadata(
        self,
        library_package_manager: models.PackageManager,
        library_escaped_name: str,
        version: str,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.LibraryVersion:
        logger.debug(
            "lib-artifact-server getting library version metadata %s %s %s",
            library_package_manager,
            library_escaped_name,
            version,
        )

        query: typing.Dict[str, str] = {
            "library_package_manager": library_package_manager.value,
            "library_escaped_name": library_escaped_name,
            "version": version,
        }
        try:
            results_page: seal_lambda_invoke.page.LimitOffsetPage[
                models.LibraryVersion
            ] = self._client.lambda_service.invoke_paginated_list_http_lambda(
                item_type=models.LibraryVersion,
                function_name=self._settings.artifact_management_lambda_name,
                path="/library_version/",
                query=query,
                offset=0,
                limit=1,
                context=request_context,
            )
        except seal_lambda_invoke.exceptions.SealLambdaInvokeHttpException as e:
            if (
                e.status_code == 400
                and e.content is not None
                and e.content.startswith("bad format for version string")
            ):
                raise exceptions.BadVersionFormat()
            else:
                raise
        if results_page.total > 1:
            raise exceptions.ArtifactManagementMoreThanOneLibraryForVersion()
        if results_page.total == 0 or len(results_page.items) == 0:
            raise exceptions.LibraryVersionNotFound()
        item = results_page.items[0]

        logger.debug(
            "lib-artifact-server got library version metadata %s %s %s %s",
            library_package_manager,
            library_escaped_name,
            version,
            item.id,
        )
        return item

    def list_all_libraries(
        self,
        ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        pretty_name: typing.Optional[str] = None,
        escaped_name: typing.Optional[str] = None,
        sealed_name: typing.Optional[str] = None,
        package_manager: typing.Optional[models.PackageManager] = None,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.Sequence[models.Library]:
        logger.debug("Pulling libraries from the artifact manager service")
        offset = 0
        more_pages = True
        library_entries: typing.List[models.Library] = []

        query = {}
        multi_value_query = {}
        if ids is not None:
            multi_value_query["id"] = [str(id_) for id_ in ids]

        if pretty_name is not None:
            query["pretty_name"] = str(pretty_name)
        if escaped_name is not None:
            query["escaped_name"] = str(escaped_name)
        if sealed_name is not None:
            query["sealed_name"] = str(sealed_name)
        if package_manager is not None:
            query["package_manager"] = package_manager.value

        while more_pages:
            response = self._client.lambda_service.invoke_paginated_list_http_lambda(
                function_name=self._settings.artifact_management_lambda_name,
                item_type=models.Library,
                path="/library/",
                multi_value_query=multi_value_query,
                query=query,
                offset=offset,
                limit=300,  # libraries are relatively small - allow more per request
                context=request_context,
            )
            library_entries.extend(response.items)
            more_pages = len(library_entries) < response.total
            offset += len(response.items)

        return library_entries

    def list_all_library_versions(
        self,
        ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        library_id: typing.Optional[uuid.UUID] = None,
        library_pretty_name: typing.Optional[str] = None,
        library_escaped_names: typing.Optional[typing.Iterable[str]] = None,
        library_sealed_name: typing.Optional[str] = None,
        library_package_manager: typing.Optional[models.PackageManager] = None,
        is_sealed: typing.Optional[bool] = None,
        is_recommended: typing.Optional[bool] = None,
        versions: typing.Optional[typing.Iterable[str]] = None,
        version_prefix: typing.Optional[str] = None,
        origin_version: typing.Optional[str] = None,
        limit: int = 300,  # library version is relatively small - allow more per request
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.Sequence[models.LibraryVersion]:
        logger.debug("Pulling library versions from the artifact manager service")
        offset = 0
        more_pages = True
        library_version_entries: typing.List[
            typing.Sequence[models.LibraryVersion]
        ] = []

        while more_pages:
            response = self.list_library_versions(
                ids=ids,
                library_id=library_id,
                library_pretty_name=library_pretty_name,
                library_escaped_names=library_escaped_names,
                library_sealed_name=library_sealed_name,
                library_package_manager=library_package_manager,
                is_sealed=is_sealed,
                is_recommended=is_recommended,
                versions=versions,
                version_prefix=version_prefix,
                origin_version=origin_version,
                offset=offset,
                request_context=request_context,
                limit=limit,
            )
            library_version_entries.append(response.items)
            offset += len(response.items)
            more_pages = offset < response.total

        return list(itertools.chain(*library_version_entries))

    def list_library_versions(
        self,
        ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        library_id: typing.Optional[uuid.UUID] = None,
        library_pretty_name: typing.Optional[str] = None,
        library_escaped_names: typing.Optional[typing.Iterable[str]] = None,
        library_sealed_name: typing.Optional[str] = None,
        library_package_manager: typing.Optional[models.PackageManager] = None,
        is_sealed: typing.Optional[bool] = None,
        is_recommended: typing.Optional[bool] = None,
        versions: typing.Optional[typing.Iterable[str]] = None,
        version_prefix: typing.Optional[str] = None,
        origin_version: typing.Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> seal_lambda_invoke.page.LimitOffsetPage[models.LibraryVersion]:
        query = {}
        if is_recommended is not None:
            query["is_recommended"] = str(is_recommended)
        if library_id is not None:
            query["library_id"] = str(library_id)
        if library_pretty_name is not None:
            query["library_pretty_name"] = library_pretty_name
        if library_sealed_name is not None:
            query["library_sealed_name"] = library_sealed_name
        if library_package_manager is not None:
            query["library_package_manager"] = library_package_manager.value
        if is_sealed is not None:
            query["is_sealed"] = str(is_sealed)
        if version_prefix is not None:
            query["version_prefix"] = version_prefix
        if origin_version is not None:
            query["origin_version"] = origin_version

        multi_value_query = {}
        if ids is not None:
            multi_value_query["id"] = [str(id_) for id_ in ids]
        if library_escaped_names is not None:
            multi_value_query["library_escaped_name"] = list(library_escaped_names)
        if versions is not None:
            multi_value_query["version"] = list(versions)

        results_page = self._client.lambda_service.invoke_paginated_list_http_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            item_type=models.LibraryVersion,
            path="/library_version/",
            multi_value_query=multi_value_query,
            query=query,
            offset=offset,
            limit=limit,
            context=request_context,
        )

        return results_page

    def search_all_library_versions(
        self,
        ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        is_sealed: typing.Optional[bool] = None,
        is_recommended: typing.Optional[bool] = None,
        version_prefix: typing.Optional[str] = None,
        library_name_or_vulnerability_contains: typing.Optional[str] = None,
        limit: int = 50,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.Sequence[models.LibraryVersion]:
        logger.debug("Pulling library versions from the artifact manager service")
        offset = 0
        more_pages = True
        library_version_entries: typing.List[
            typing.Sequence[models.LibraryVersion]
        ] = []

        while more_pages:
            response = self.search_library_versions(
                ids=ids,
                is_sealed=is_sealed,
                is_recommended=is_recommended,
                version_prefix=version_prefix,
                library_name_or_vulnerability_contains=library_name_or_vulnerability_contains,
                offset=offset,
                request_context=request_context,
                limit=limit,
            )
            library_version_entries.append(response.items)
            offset += len(response.items)
            more_pages = offset < response.total

        return list(itertools.chain(*library_version_entries))

    def search_library_versions(
        self,
        ids: typing.Optional[typing.Iterable[uuid.UUID]] = None,
        is_sealed: typing.Optional[bool] = None,
        is_recommended: typing.Optional[bool] = None,
        version_prefix: typing.Optional[str] = None,
        library_name_or_vulnerability_contains: typing.Optional[str] = None,
        sort_by: typing.Optional[typing.List[str]] = None,
        offset: int = 0,
        limit: int = 50,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> seal_lambda_invoke.page.LimitOffsetPage[models.LibraryVersion]:
        query = {}
        if is_recommended is not None:
            query["is_recommended"] = str(is_recommended)
        if is_sealed is not None:
            query["is_sealed"] = str(is_sealed)
        if version_prefix is not None:
            query["version_prefix"] = version_prefix
        if library_name_or_vulnerability_contains is not None:
            query[
                "library_name_or_vulnerability_contains"
            ] = library_name_or_vulnerability_contains

        multi_value_query = {}
        if ids is not None:
            multi_value_query["id"] = [str(id_) for id_ in ids]
        if sort_by is not None:
            multi_value_query["sort_by"] = sort_by

        results_page = self._client.lambda_service.invoke_paginated_list_http_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            item_type=models.LibraryVersion,
            path="/library_version/search",
            multi_value_query=multi_value_query,
            query=query,
            offset=offset,
            limit=limit,
            context=request_context,
        )

        return results_page

    def update_library_version(
        self,
        id: uuid.UUID,
        library_version_update: models.LibraryVersionUpdate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.LibraryVersion:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/library_version/{id}",
            method="PUT",
            body=library_version_update.model_dump_json().encode(),
            context=request_context,
        )
        if response is None:
            raise exceptions.LibraryVersionUpdateFailed()
        return models.LibraryVersion.model_validate_json(response)

    def list_all_vulnerabilities(
        self,
        ids: typing.Optional[typing.List[uuid.UUID]] = None,
        library_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        library_version_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        vulnerability_impact_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        library_escaped_name: typing.Optional[str] = None,
        library_package_manager: typing.Optional[models.PackageManager] = None,
        impacted_library_version: typing.Optional[str] = None,
        cve: typing.Optional[str] = None,
        snyk_id: typing.Optional[str] = None,
        github_advisory_id: typing.Optional[str] = None,
        malicious_id: typing.Optional[str] = None,
        is_fixed: typing.Optional[bool] = None,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.Sequence[models.Vulnerability]:
        logger.debug("Pulling vulnerabilities from the artifact manager service")
        offset = 0
        more_pages = True
        vulnerability_entries: typing.List[models.Vulnerability] = []

        query = {}
        multi_value_query = {}
        if library_escaped_name is not None:
            query["library_escaped_name"] = library_escaped_name
        if library_package_manager is not None:
            query["library_package_manager"] = library_package_manager.value
        if impacted_library_version is not None:
            query["impacted_library_version"] = impacted_library_version
        if cve is not None:
            query["cve"] = cve
        if snyk_id is not None:
            query["snyk_id"] = snyk_id
        if github_advisory_id is not None:
            query["github_advisory_id"] = github_advisory_id
        if malicious_id is not None:
            query["malicious_id"] = malicious_id
        if is_fixed is not None:
            query["is_fixed"] = str(is_fixed)

        if ids is not None:
            multi_value_query["id"] = [str(id_) for id_ in ids]
        if library_ids is not None:
            multi_value_query["library_id"] = [
                str(library_id_) for library_id_ in library_ids
            ]
        if library_version_ids is not None:
            multi_value_query["library_version_id"] = [
                str(library_version_id) for library_version_id in library_version_ids
            ]
        if vulnerability_impact_ids is not None:
            multi_value_query["vulnerability_impact_id"] = [
                str(vulnerability_impact_id_)
                for vulnerability_impact_id_ in vulnerability_impact_ids
            ]

        while more_pages:
            response = self._client.lambda_service.invoke_paginated_list_http_lambda(
                function_name=self._settings.artifact_management_lambda_name,
                item_type=models.Vulnerability,
                path="/vulnerability/",
                query=query,
                multi_value_query=multi_value_query,
                offset=offset,
                limit=300,  # vulnerability are relatively small - allow more per request
                context=request_context,
            )
            vulnerability_entries.extend(response.items)
            more_pages = len(vulnerability_entries) < response.total
            offset += len(response.items)

        return vulnerability_entries

    def list_all_vulnerability_impacts(
        self,
        library_version_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        library_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        vulnerability_ids: typing.Optional[typing.List[uuid.UUID]] = None,
        impacted_version: typing.Optional[str] = None,
        is_fixed: typing.Optional[bool] = None,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> typing.Sequence[models.VulnerabilityImpact]:
        logger.debug(
            "Pulling all the vulnerability impacts from the artifact manager service"
        )
        offset = 0
        more_pages = True
        vulnerability_impact_entries: typing.List[models.VulnerabilityImpact] = []
        multi_value_query = {}
        if library_version_ids is not None:
            multi_value_query["library_version_id"] = [
                str(library_version_id_) for library_version_id_ in library_version_ids
            ]
        if library_ids is not None:
            multi_value_query["library_id"] = [
                str(library_id_) for library_id_ in library_ids
            ]
        if vulnerability_ids is not None:
            multi_value_query["vulnerability_id"] = [
                str(vulnerability_id_) for vulnerability_id_ in vulnerability_ids
            ]

        query = {}
        if impacted_version is not None:
            query["impacted_version"] = impacted_version
        if is_fixed is not None:
            query["is_fixed"] = str(is_fixed)

        while more_pages:
            response = self._client.lambda_service.invoke_paginated_list_http_lambda(
                function_name=self._settings.artifact_management_lambda_name,
                item_type=models.VulnerabilityImpact,
                path="/vulnerability_impact/",
                query=query,
                multi_value_query=multi_value_query,
                offset=offset,
                limit=300,  # vulnerability impacts are relatively small - allow more per request
                context=request_context,
            )
            vulnerability_impact_entries.extend(response.items)
            more_pages = len(vulnerability_impact_entries) < response.total
            offset += len(response.items)

        return vulnerability_impact_entries

    def create_library(
        self,
        library_create: models.LibraryCreate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Library:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path="/library/",
            method="POST",
            body=library_create.model_dump_json().encode(),
            context=request_context,
        )
        if response is None:
            raise exceptions.LibraryCreateFailed()
        return models.Library.model_validate_json(response)

    def create_library_version(
        self,
        library_version_create: models.LibraryVersionCreate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.LibraryVersion:
        try:
            response = self._client.lambda_service.invoke_http_proxy_lambda(
                function_name=self._settings.artifact_management_lambda_name,
                path="/library_version/",
                method="POST",
                body=library_version_create.model_dump_json().encode(),
                context=request_context,
            )
        except seal_lambda_invoke.exceptions.SealLambdaInvokeHttpException as e:
            if (
                e.status_code == 400
                and e.content == "The library version already exists"
            ):
                raise exceptions.LibraryVersionAlreadyExists()
            raise
        if response is None:
            raise exceptions.LibraryVersionCreateFailed()
        return models.LibraryVersion.model_validate_json(response)

    def create_vulnerability(
        self,
        vulnerability_create: models.VulnerabilityCreate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Vulnerability:
        try:
            response = self._client.lambda_service.invoke_http_proxy_lambda(
                function_name=self._settings.artifact_management_lambda_name,
                path="/vulnerability/",
                method="POST",
                body=vulnerability_create.model_dump_json().encode(),
                context=request_context,
            )
        except seal_lambda_invoke.exceptions.SealLambdaInvokeHttpException as e:
            if e.status_code == 400 and e.content == "The vulnerability already exists":
                raise exceptions.VulnerabilityAlreadyExists()
            raise
        if response is None:
            raise exceptions.VulnerabilityCreateFailed()
        return models.Vulnerability.model_validate_json(response)

    def create_vulnerability_impact(
        self,
        vulnerability_impact_create: models.VulnerabilityImpactCreate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.VulnerabilityImpact:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path="/vulnerability_impact/",
            method="POST",
            body=vulnerability_impact_create.model_dump_json().encode(),
            context=request_context,
        )
        if response is None:
            raise exceptions.VulnerabilityImpactCreateFailed()
        return models.VulnerabilityImpact.model_validate_json(response)

    def create_artifact(
        self,
        artifact_create: models.ArtifactCreate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Artifact:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path="/artifact/",
            method="POST",
            body=artifact_create.model_dump_json().encode(),
            context=request_context,
        )
        if response is None:
            raise exceptions.ArtifactCreateFailed()
        return models.Artifact.model_validate_json(response)

    def update_vulnerability(
        self,
        id: uuid.UUID,
        vulnerability_update: models.VulnerabilityUpdate,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> models.Vulnerability:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/vulnerability/{id}",
            method="PUT",
            body=vulnerability_update.model_dump_json().encode(),
            context=request_context,
        )
        if response is None:
            raise exceptions.VulnerabilityUpdateFailed()
        return models.Vulnerability.model_validate_json(response)

    def delete_vulnerability(
        self,
        id: uuid.UUID,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> None:
        self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/vulnerability/{id}",
            method="DELETE",
            context=request_context,
        )

    def delete_vulnerability_impact(
        self,
        id: uuid.UUID,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> None:
        self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/vulnerability_impact/{id}",
            method="DELETE",
            context=request_context,
        )

    def delete_library_version(
        self,
        id: uuid.UUID,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> None:
        self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/library_version/{id}",
            method="DELETE",
            context=request_context,
        )

    def delete_library(
        self,
        id: uuid.UUID,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> None:
        self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/library/{id}",
            method="DELETE",
            context=request_context,
        )

    def delete_artifact(
        self,
        id: uuid.UUID,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> None:
        self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path=f"/artifact/{id}",
            method="DELETE",
            context=request_context,
        )

    def bulk_query_library_versions(
        self,
        library_identifiers: models.PublicLibraryIdentifierList,
        is_fix: typing.Optional[bool] = None,
        request_context: typing.Optional[
            seal_lambda_invoke.context.RequestContext
        ] = None,
    ) -> seal_lambda_invoke.page.LimitOffsetPage[models.LibraryVersion]:
        response = self._client.lambda_service.invoke_http_proxy_lambda(
            function_name=self._settings.artifact_management_lambda_name,
            path="/library_version/bulk_query",
            method="POST",
            query={"is_fix": str(is_fix)} if is_fix is not None else {},
            body=library_identifiers.model_dump_json().encode(),
            context=request_context,
        )
        return seal_lambda_invoke.page.LimitOffsetPage[
            models.LibraryVersion
        ].model_validate_json(response)
