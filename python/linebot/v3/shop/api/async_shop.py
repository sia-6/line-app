# coding: utf-8

"""
    Mission Stickers API

    This document describes LINE Mission Stickers API.  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import re  # noqa: F401
import io
import warnings

from pydantic.v1 import validate_arguments, ValidationError
from typing_extensions import Annotated
from typing import overload, Optional, Union, Awaitable

from linebot.v3.shop.models.mission_sticker_request import MissionStickerRequest

from linebot.v3.shop.async_api_client import AsyncApiClient
from linebot.v3.shop.api_response import ApiResponse
from linebot.v3.shop.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class AsyncShop(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = AsyncApiClient.get_default()
        self.api_client = api_client
        self.line_base_path = "https://api.line.me"


    @overload
    async def mission_sticker_v3(self, mission_sticker_request : MissionStickerRequest, **kwargs) -> None:  # noqa: E501
        ...

    @overload
    def mission_sticker_v3(self, mission_sticker_request : MissionStickerRequest, async_req: Optional[bool]=True, **kwargs) -> None:  # noqa: E501
        ...

    @validate_arguments
    def mission_sticker_v3(self, mission_sticker_request : MissionStickerRequest, async_req: Optional[bool]=None, **kwargs) -> Union[None, Awaitable[None]]:  # noqa: E501
        """mission_sticker_v3  # noqa: E501

        Sends a mission sticker.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.mission_sticker_v3(mission_sticker_request, async_req=True)
        >>> result = thread.get()

        :param mission_sticker_request: (required)
        :type mission_sticker_request: MissionStickerRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            raise ValueError("Error! Please call the mission_sticker_v3_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data")
        if async_req is not None:
            kwargs['async_req'] = async_req
        return self.mission_sticker_v3_with_http_info(mission_sticker_request, **kwargs)  # noqa: E501

    @validate_arguments
    def mission_sticker_v3_with_http_info(self, mission_sticker_request : MissionStickerRequest, **kwargs) -> ApiResponse:  # noqa: E501
        """mission_sticker_v3  # noqa: E501

        Sends a mission sticker.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.mission_sticker_v3_with_http_info(mission_sticker_request, async_req=True)
        >>> result = thread.get()

        :param mission_sticker_request: (required)
        :type mission_sticker_request: MissionStickerRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """

        _host = self.line_base_path
        _params = locals()

        _all_params = [
            'mission_sticker_request'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method mission_sticker_v3" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        if _params['mission_sticker_request'] is not None:
            _body_params = _params['mission_sticker_request']

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = ['Bearer']  # noqa: E501

        _response_types_map = {}

        return self.api_client.call_api(
            '/shop/v3/mission', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
