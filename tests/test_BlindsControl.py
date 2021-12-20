import mock
import pytest
from datetime import datetime, timedelta, time
from BlindsControl import BlindsControl, BlindsControlConfiguration, GlobalBlindsControl
import logging
from unittest.mock import ANY
from freezegun import freeze_time
import uuid

class TestBlindsControl:

    @pytest.fixture
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def blindscontrol(self, given_that):
        blindscontrol = BlindsControl(
            None, BlindsControl.__name__, None, None, None, None, None)
        blindscontrolconfig = BlindsControlConfiguration(
            None, BlindsControlConfiguration.__name__, None, None, None, None, None)

        # Set initial state
        coverlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for cover in coverlist:
            given_that.state_of(f"cover.{cover}").is_set_to(
                "closed", {'friendly_name': f"{cover}", 'current_position': 0, 'value_id': cover})
            for varbool in blindscontrolconfig.variables_boolean:
                print(f"input_boolean.control_blinds_{cover}_{varbool}")
                given_that.state_of(
                    f"input_boolean.control_blinds_{cover}_{varbool}").is_set_to("off")

            for vardate in blindscontrolconfig.variables_datetime:
                print(f"input_datetime.control_blinds_{cover}_{vardate}")
                given_that.state_of(
                    f"input_datetime.control_blinds_{cover}_{vardate}").is_set_to("00:00:00")

            for varnumb in blindscontrolconfig.variables_number:
                print(f"input_number.control_blinds_{cover}_{varnumb}")
                given_that.state_of(
                    f"input_number.control_blinds_{cover}_{varnumb}").is_set_to("100")

        for varboolglob in blindscontrolconfig.variables_boolean_global:
            print(f"input_boolean.control_blinds_{varboolglob}")
            given_that.state_of(
                f"input_boolean.control_blinds_{varboolglob}").is_set_to("off")

        given_that.state_of(
            "input_boolean.control_blinds_configuration").is_set_to("off")
        given_that.state_of("binary_sensor.workday_sensor").is_set_to("on")

        # set namespace
        blindscontrol.set_namespace(None)

        # passed args
        given_that.passed_arg('debug').is_set_to('True')

        blindscontrol.initialize()
        given_that.mock_functions_are_cleared()
        return blindscontrol

    # Blindcontrol Inititalize
    # Test if alle handles are created and all config variables are watched
    @freeze_time("2019-10-16 12:32:02", tz_offset=2)
    def test_initialize(self, given_that, blindscontrol, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        
        blindscontrolconfig = BlindsControlConfiguration(
            None, BlindsControlConfiguration.__name__, None, None, None, None, None)

        #set inital state of variables
        coverlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for cover in coverlist:
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")   
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on") 
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")

        blindscontrol.initialize()

        # Watch alle config variables for changes
        for cover in coverlist:
            given_that.state_of(f"cover.{cover}").is_set_to(
                "closed", {'friendly_name': f"{cover}", 'current_position': 0, 'value_id': cover})
            for varbool in blindscontrolconfig.variables_boolean:
                assert_that(blindscontrol).listens_to.state(f"input_boolean.control_blinds_{cover}_{varbool}", entityid=f"{cover}", duration=10) \
                .with_callback(blindscontrol._config_change)

            for vardate in blindscontrolconfig.variables_datetime:
                assert_that(blindscontrol).listens_to.state(f"input_datetime.control_blinds_{cover}_{vardate}", entityid=f"{cover}",duration=10) \
                .with_callback(blindscontrol._config_change)

            for varnumb in blindscontrolconfig.variables_number:
                assert_that(blindscontrol).listens_to.state(f"input_number.control_blinds_{cover}_{varnumb}", entityid=f"{cover}", duration=10) \
                .with_callback(blindscontrol._config_change)

        for varboolglob in blindscontrolconfig.variables_boolean_global:
            assert_that(blindscontrol).listens_to.state(f"input_boolean.control_blinds_{varboolglob}", duration=10) \
                .with_callback(blindscontrol._config_change_global)

        #check if handles are created
        for cover in coverlist:
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._choose_open_blinds_method)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._choose_close_blinds_method)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._open_blinds_cooldown)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._close_blinds_cooldown)
        
    # Cancel all handles
    # control_blinds_enable_global is off
    @freeze_time("2019-10-16 12:32:02", tz_offset=2)
    def test_initialize_control_blinds_enable_global_off(self, given_that, blindscontrol, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        #blindscontrolconfig = BlindsControlConfiguration(
        #    None, BlindsControlConfiguration.__name__, None, None, None, None, None)
        
        #set inital state of variables
        coverlist = ['living_room', 'guest_room', 'parents_room', 'kids_room']
        for cover in coverlist:
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")   
            given_that.state_of(
                f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on") 
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")

        blindscontrol.initialize()

        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("off")

        #copy handledict
        #coverdict = blindscontrol._coverdict.copy()
        handlelist = list()
        for cover in coverlist:
            handlelist.append(blindscontrol._get_handle(cover, 'cb_handle'))
            handlelist.append(blindscontrol._get_handle(cover, 'ob_handle'))
            handlelist.append(blindscontrol._get_handle(cover, 'obcd_handle'))
            handlelist.append(blindscontrol._get_handle(cover, 'cbcd_handle'))
        
        blindscontrol.cancel_timer = mock.MagicMock()
        blindscontrol._config_change_global('input_boolean.control_blinds_enable_global', 'state', 'on', 'off', {})
        
        #now we check if all "old" handles have been canceled
        for handle in handlelist:
            #blindscontrol.cancel_timer.assert_any_call(handle)
            blindscontrol.cancel_timer.called_with(handle)

        #check if handles are created
        for cover in coverlist:
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._choose_open_blinds_method)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._choose_close_blinds_method)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._open_blinds_cooldown)
            assert_that(blindscontrol).registered.run_at(datetime.now() + timedelta(seconds=5), entityid=f"{cover}").with_callback(blindscontrol._close_blinds_cooldown)
    
    # React on Config Change
    # Open Cover
    def test_config_change_control_blinds_global_enabled_open_cover_enabled(self, given_that, blindscontrol, assert_that, caplog, time_travel):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        blindscontrol._config_change(
            f"cover.{cover}", None, False, True, {"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(ANY, entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    # React on Config Change
    # Close Cover
    def test_config_change_control_blinds_global_enabled_close_cover_enabled(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        blindscontrol._config_change(
            f"cover.{cover}", None, False, True, {"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(ANY, entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    # React on Config Change
    # Cooldown during night
    def test_config_change_control_blinds_global_enabled_cooldown_global_enabled_cooldown_cover_global_enabled(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        blindscontrol._config_change(
            f"cover.{cover}", None, False, True, {"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(ANY, entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown)
        assert_that(blindscontrol) \
            .registered.run_at(ANY, entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown)

    # Open Cover on Sunrise
    # _choose_open_blinds_method
    def test_choose_open_blinds_method_sunrise(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_sunsetsunrise').is_set_to("on")
        blindscontrol._open_blinds_sun = mock.MagicMock()
        blindscontrol._choose_open_blinds_method({"entityid": cover})
        assert blindscontrol._open_blinds_sun.called

    # Open Cover on Time
    # _choose_open_blinds_method
    def test_choose_open_blinds_method_time(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_sunsetsunrise').is_set_to("off")
        blindscontrol._open_blinds_time = mock.MagicMock()
        blindscontrol._choose_open_blinds_method({"entityid": cover})
        assert blindscontrol._open_blinds_time.called

    # CLose Cover on Sunrise
    # _choose_close_blinds_method
    def test_choose_close_blinds_method_sunrise(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_sunsetsunrise').is_set_to("on")
        blindscontrol._close_blinds_sun = mock.MagicMock()
        blindscontrol._choose_close_blinds_method({"entityid": cover})
        assert blindscontrol._close_blinds_sun.called

    # Close Cover on Time
    # _choose_close_blinds_method
    def test_choose_close_blinds_method_time(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_sunsetsunrise').is_set_to("off")
        blindscontrol._close_blinds_time = mock.MagicMock()
        blindscontrol._choose_close_blinds_method({"entityid": cover})
        assert blindscontrol._close_blinds_time.called

    # Cooldown during night
    # close blinds
    # time for close cover is before normal time to open cover
    # time to close cover is in the future
    # current time is between 0 an 12
    # -> schedule Close Cover
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test_close_blinds_cooldown_0_12(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")
        time_cooldown_during_night_close = today + timedelta(hours=5)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_close').is_set_to(time_cooldown_during_night_close, {
            "hour": time_cooldown_during_night_close.hour, "minute": time_cooldown_during_night_close.minute, "second": time_cooldown_during_night_close.second})
        blindscontrol._set_variable(
            cover, "time_open_blinds", today + timedelta(hours=8))

        blindscontrol._close_blinds_cooldown({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(time_cooldown_during_night_close, entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown_)

    # Cooldown during night
    # close blinds
    # time for close cover is before normal time to open cover
    # time to close cover is in the future
    # current time is between 12 an 24
    # -> schedule Close Cover
    @freeze_time("2019-10-16 12:32:02", tz_offset=2)
    def test_close_blinds_cooldown_12_24(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")
        time_cooldown_during_night_close = today + timedelta(hours=5)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_close').is_set_to(time_cooldown_during_night_close, {
            "hour": time_cooldown_during_night_close.hour, "minute": time_cooldown_during_night_close.minute, "second": time_cooldown_during_night_close.second})
        # da die aktuelle Zeit nach der open time ist wurde die open time schon auf die Zeit vom nächsten Tag gesetzt
        blindscontrol._set_variable(
            cover, "time_open_blinds", today + timedelta(days=1, hours=8))

        blindscontrol._close_blinds_cooldown({"entityid": cover})
        # wenn die aktuelle Stunde zwischen 12 und 24 Uhr liegt
        # und die close time zwischen 0 und 12 bezieht sich die Zeit auf den nächsten Tag
        time_cooldown_during_night_close += timedelta(days=1)
        assert_that(blindscontrol) \
            .registered.run_at(time_cooldown_during_night_close, entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown_)

    # Cooldown during night
    # close blinds
    # time for close cover is before normal time to open cover
    # time to close cover is in the future
    # current time is after time to close cover
    # -> Recheck 5 min after midnight
    @freeze_time("2019-10-16 07:02:02", tz_offset=2)
    def test_close_blinds_cooldown_time_passed(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")
        time_cooldown_during_night_close = today + timedelta(hours=5)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_close').is_set_to(time_cooldown_during_night_close, {
            "hour": time_cooldown_during_night_close.hour, "minute": time_cooldown_during_night_close.minute, "second": time_cooldown_during_night_close.second})
        blindscontrol._set_variable(
            cover, "time_open_blinds", today + timedelta(hours=10))

        blindscontrol._close_blinds_cooldown({"entityid": cover})
        # wir warten bis zum nächsten Tag, dann neu prüfen
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1, minutes=5), entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown)

    # Cooldown during night
    # close blinds
    # time for close cover is after normal time to open cover
    # time to close cover is in the future
    # -> recheck in 5 minutes
    @freeze_time("2019-10-16 07:02:02", tz_offset=2)
    def test_close_blinds_cooldown_wrong_config(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_openblinds').is_set_to("on")
        time_cooldown_during_night_close = today + timedelta(hours=10)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_close').is_set_to(time_cooldown_during_night_close, {
            "hour": time_cooldown_during_night_close.hour, "minute": time_cooldown_during_night_close.minute, "second": time_cooldown_during_night_close.second})
        blindscontrol._set_variable(
            cover, "time_open_blinds", today + timedelta(hours=5))

        blindscontrol._close_blinds_cooldown({"entityid": cover})
        # erneut in 5min prüfen
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown)

    # Cooldown during night
    # open blinds
    # time for open cover is after normal time to close cover
    # time to open cover is in the future
    # current time is between 0 an 12
    # -> schedule Open Cover
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def test_open_blinds_cooldown_0_12(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
        time_cooldown_during_night_open = today + timedelta(hours=23)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_open').is_set_to(time_cooldown_during_night_open, {
            "hour": time_cooldown_during_night_open.hour, "minute": time_cooldown_during_night_open.minute, "second": time_cooldown_during_night_open.second})
        blindscontrol._set_variable(
            cover, "time_close_blinds", today + timedelta(hours=20))

        blindscontrol._open_blinds_cooldown({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(time_cooldown_during_night_open, entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown_)

    # Cooldown during night
    # open blinds
    # time for open cover is after normal time to close cover
    # time to open cover is in the future
    # current time is between 12 an 24
    # -> schedule Open Cover
    @freeze_time("2019-10-16 12:02:02", tz_offset=2)
    def test_open_blinds_cooldown_12_24(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
        time_cooldown_during_night_open = today + timedelta(hours=23)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_open').is_set_to(time_cooldown_during_night_open, {
            "hour": time_cooldown_during_night_open.hour, "minute": time_cooldown_during_night_open.minute, "second": time_cooldown_during_night_open.second})
        blindscontrol._set_variable(
            cover, "time_close_blinds", today + timedelta(hours=20))

        blindscontrol._open_blinds_cooldown({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(time_cooldown_during_night_open, entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown_)

    # Cooldown during night
    # open blinds
    # time for open cover is after normal time to close cover
    # time to open cover is in the past
    # current time is after open cover time
    # -> recheck 5 min after midnight
    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    def test_open_blinds_cooldown_time_passed(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
        time_cooldown_during_night_open = today + timedelta(hours=21)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_open').is_set_to(time_cooldown_during_night_open, {
            "hour": time_cooldown_during_night_open.hour, "minute": time_cooldown_during_night_open.minute, "second": time_cooldown_during_night_open.second})
        blindscontrol._set_variable(
            cover, "time_close_blinds", today + timedelta(hours=20))

        blindscontrol._open_blinds_cooldown({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1, minutes=5), entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown)

    # Cooldown during night
    # open blinds
    # time for open cover is befor normal time to close cover
    # time to open cover is in the future
    # recheck in 5 min
    @freeze_time("2019-10-16 16:02:02", tz_offset=2)
    def test_open_blinds_cooldown_wrong_config(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # now the real test can start
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_cooldown_during_night').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_cooldown_during_night_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_global').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_closeblinds').is_set_to("on")
        time_cooldown_during_night_open = today + timedelta(hours=19)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_cooldown_during_night_open').is_set_to(time_cooldown_during_night_open, {
            "hour": time_cooldown_during_night_open.hour, "minute": time_cooldown_during_night_open.minute, "second": time_cooldown_during_night_open.second})
        blindscontrol._set_variable(
            cover, "time_close_blinds", today + timedelta(hours=20))

        blindscontrol._open_blinds_cooldown({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # Sunsetday is current day
    # sunset + offset is greater than Latesttimedown
    # latesttimedown has passed
    # -> recheck in 5 minutes _choose_close_blinds_method
    def test_close_blinds_sun_latesttimedown_passed(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set offset
        offset_blinds_down_after_sunset = today + \
            timedelta(hours=1, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_offset_blinds_down_after_sunset').is_set_to(offset_blinds_down_after_sunset, {
            "hour": offset_blinds_down_after_sunset.hour, "minute": offset_blinds_down_after_sunset.minute, "second": offset_blinds_down_after_sunset.second})

        # set sunsettime
        blindscontrol.sunset = mock.MagicMock(
            return_value=today + timedelta(hours=21, minutes=30))

        # set latesttimedown
        latest_time_blinds_down = today + \
            timedelta(hours=22, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_latest_time_blinds_down').is_set_to(latest_time_blinds_down, {
            "hour": latest_time_blinds_down.hour, "minute": latest_time_blinds_down.minute, "second": latest_time_blinds_down.second})

        blindscontrol._close_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 17:02:02", tz_offset=2)
    # Sunsetday is current day
    # sunset + offset is greater than Latesttimedown
    # current time before latesttimedown
    # -> schedule close blinds at latesttimedown (_close_blinds)
    def test_close_blinds_sun_latesttimedown(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set offset
        offset_blinds_down_after_sunset = today + \
            timedelta(hours=1, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_offset_blinds_down_after_sunset').is_set_to(offset_blinds_down_after_sunset, {
            "hour": offset_blinds_down_after_sunset.hour, "minute": offset_blinds_down_after_sunset.minute, "second": offset_blinds_down_after_sunset.second})

        # set sunsettime
        blindscontrol.sunset = mock.MagicMock(
            return_value=today + timedelta(hours=19, minutes=30))

        # set latesttimedown
        latest_time_blinds_down = today + \
            timedelta(hours=20, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_latest_time_blinds_down').is_set_to(latest_time_blinds_down, {
            "hour": latest_time_blinds_down.hour, "minute": latest_time_blinds_down.minute, "second": latest_time_blinds_down.second})

        blindscontrol._close_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(latest_time_blinds_down, entityid=cover) \
            .with_callback(blindscontrol._close_blinds)

    @freeze_time("2019-10-16 17:02:02", tz_offset=2)
    # Sunsetday is current day
    # sunset + offset is smaller than Latesttimedown
    # current time before sunset + offset
    # -> schedule close blinds at sunset + offset (_close_blinds)
    def test_close_blinds_sun(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set offset
        offset = timedelta(hours=1, minutes=0, seconds=0)
        offset_blinds_down_after_sunset = today + offset
        given_that.state_of(f'input_datetime.control_blinds_{cover}_offset_blinds_down_after_sunset').is_set_to(offset_blinds_down_after_sunset, {
            "hour": offset_blinds_down_after_sunset.hour, "minute": offset_blinds_down_after_sunset.minute, "second": offset_blinds_down_after_sunset.second})

        # set sunsettime
        sunsettime = today + timedelta(hours=19, minutes=30)
        blindscontrol.sunset = mock.MagicMock(return_value=sunsettime)

        # set latesttimedown
        latest_time_blinds_down = today + \
            timedelta(hours=22, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_latest_time_blinds_down').is_set_to(latest_time_blinds_down, {
            "hour": latest_time_blinds_down.hour, "minute": latest_time_blinds_down.minute, "second": latest_time_blinds_down.second})

        blindscontrol._close_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(sunsettime + offset, entityid=cover) \
            .with_callback(blindscontrol._close_blinds)

    @freeze_time("2019-10-16 17:02:02", tz_offset=2)
    # Sunsetday < today
    # we should never get here!
    # -> reschedule close blinds (_choose_close_blinds_method)
    def test_close_blinds_sun_sunset_before_today(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set offset
        offset = timedelta(hours=1, minutes=0, seconds=0)
        offset_blinds_down_after_sunset = today + offset
        given_that.state_of(f'input_datetime.control_blinds_{cover}_offset_blinds_down_after_sunset').is_set_to(offset_blinds_down_after_sunset, {
            "hour": offset_blinds_down_after_sunset.hour, "minute": offset_blinds_down_after_sunset.minute, "second": offset_blinds_down_after_sunset.second})

        # set sunsettime
        sunsettime = today + timedelta(days=-1, hours=19, minutes=30)
        blindscontrol.sunset = mock.MagicMock(return_value=sunsettime)

        # set latesttimedown
        latest_time_blinds_down = today + \
            timedelta(hours=22, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_latest_time_blinds_down').is_set_to(latest_time_blinds_down, {
            "hour": latest_time_blinds_down.hour, "minute": latest_time_blinds_down.minute, "second": latest_time_blinds_down.second})

        blindscontrol._close_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 17:02:02", tz_offset=2)
    # Sunsetday > today
    # -> reschedule to check 5 min after midnight (_choose_close_blinds_method)
    def test_close_blinds_sun_sunset_after_today(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set offset
        offset = timedelta(hours=1, minutes=0, seconds=0)
        offset_blinds_down_after_sunset = today + offset
        given_that.state_of(f'input_datetime.control_blinds_{cover}_offset_blinds_down_after_sunset').is_set_to(offset_blinds_down_after_sunset, {
            "hour": offset_blinds_down_after_sunset.hour, "minute": offset_blinds_down_after_sunset.minute, "second": offset_blinds_down_after_sunset.second})

        # set sunsettime
        sunsettime = today + timedelta(days=1, hours=19, minutes=30)
        blindscontrol.sunset = mock.MagicMock(return_value=sunsettime)

        # set latesttimedown
        latest_time_blinds_down = today + \
            timedelta(hours=22, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_latest_time_blinds_down').is_set_to(latest_time_blinds_down, {
            "hour": latest_time_blinds_down.hour, "minute": latest_time_blinds_down.minute, "second": latest_time_blinds_down.second})

        blindscontrol._close_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1, minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    # Close blinds on time
    # current time before time to close covers
    # -> schedule close blinds (_close_blinds)
    def test_close_blinds_time_(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set time to close cover
        closeblinds_on_time = today + timedelta(hours=20, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_closeblinds_on_time').is_set_to(closeblinds_on_time, {
            "hour": closeblinds_on_time.hour, "minute": closeblinds_on_time.minute, "second": closeblinds_on_time.second})

        blindscontrol._close_blinds_time(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(closeblinds_on_time, entityid=cover) \
            .with_callback(blindscontrol._close_blinds)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # Close blinds on time
    # current time after time to close covers
    # -> schedule close blinds (_close_blinds)
    def test_close_blinds_time_(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set time to close cover
        closeblinds_on_time = today + timedelta(hours=20, minutes=0, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_closeblinds_on_time').is_set_to(closeblinds_on_time, {
            "hour": closeblinds_on_time.hour, "minute": closeblinds_on_time.minute, "second": closeblinds_on_time.second})

        blindscontrol._close_blinds_time(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1, minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)


# _close_blinds
# Fall1: Globad PD off, Cover PD on, Person da -> close cover
# Fall2: GLobal PD on, Cover PD off, Person da -> close cover
# Fall3: GLobal PD on, Cover PD on, Person da -> cover nicht schließen
# Fall4: Globad PD off, Cover PD on, Person nicht da -> close cover
# Fall5: GLobal PD on, Cover PD off, Person nicht da -> close cover
# Fall6: GLobal PD on, Cover PD on, Person nicht da -> cover  schließen

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall1: Global PD off, Cover PD on, Person da -> close cover
    def test_close_blinds_gpd_off_coverpd_on_pd_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("off")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall2: Global PD on, Cover PD off, Person da -> close cover
    def test_close_blinds_gpd_on_coverpd_off_pd_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("off")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("on")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall3: Global PD on, Cover PD on, Person da -> do not close cover
    def test_close_blinds_gpd_on_coverpd_on_pd_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("on")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was_not.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall4: Global PD off, Cover PD on, Person nicht da -> close cover
    def test_close_blinds_gpd_off_coverpd_on_pd_not_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("off")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'not home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall5: Global PD on, Cover PD off, Person nicht da -> close cover
    def test_close_blinds_gpd_on_coverpd_off_pd_not_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("off")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("on")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'not home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds
    # Fall6: Global PD on, Cover PD on, Person nicht da -> close cover
    def test_close_blinds_gpd_on_coverpd_on_pd_not_home(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # init
        given_that.state_of(
            f'input_boolean.control_blinds_{cover}_use_pd_on_close').is_set_to("on")
        given_that.state_of(
            f'input_boolean.control_blinds_enable_pd_global').is_set_to("on")
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        # Person 'Parent' is hat home
        given_that.state_of('person.jondoe').is_set_to(
            'not home', {'friendly_name': 'Jon'})

        blindscontrol._close_blinds({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_close_blinds_method)

# _close_blinds_cooldown_
# Fall 1: current_position > 0 -> close cover
# Fall 2: current_position = 0 -> do not close cover
    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds_cooldown_
    # Fall 1: current_position > 0 -> close cover
    def test_close_blinds_cooldown__cover_open(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # init
        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100})

        blindscontrol._close_blinds_cooldown_({"entityid": cover})
        assert_that(
            'cover/close_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown)

    @freeze_time("2019-10-16 21:02:02", tz_offset=2)
    # _close_blinds_cooldown_
    # Fall 2: current_position = 0 -> do not close cover
    def test_close_blinds_cooldown__cover_open(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        blindscontrol._close_blinds_cooldown_({"entityid": cover})
        assert_that(
            'cover/close_cover').was_not.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._close_blinds_cooldown)


    @freeze_time("2019-10-16 08:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall1: during week, sunriseday=today, sunrisetime < earliest_time_blinds_up, sunrisetime < datetime.now(), -> _choose_open_blinds_method
    def test_open_blinds_sun_case1(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=7, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall2: during week, sunriseday=today, sunrisetime < earliest_time_blinds_up, sunrisetime >= datetime.now(), -> _open_blinds
    def test_open_blinds_sun_case2(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=7, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(hours=8), entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 09:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall3: during week, sunriseday=today, sunrisetime > earliest_time_blinds_up, sunrisetime < datetime.now(), -> _choose_open_blinds_method
    def test_open_blinds_sun_case3(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall4: during week, sunriseday=today, sunrisetime > earliest_time_blinds_up, sunrisetime >= datetime.now(), -> _open_blinds
    def test_open_blinds_sun_case4(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(hours=8, minutes=30), entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 09:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall5: sunriseday<today, -> _choose_open_blinds_method
    def test_open_blinds_sun_case5(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(days=-1) + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 09:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall6: sunriseday>today, -> _choose_open_blinds_method
    def test_open_blinds_sun_case6(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(days=1) + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("on")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1) + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 08:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall7: on weekend, sunriseday=today, sunrisetime < earliest_time_blinds_up, sunrisetime < datetime.now(), -> _choose_open_blinds_method
    def test_open_blinds_sun_case7(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=7, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("off")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall8: on weekend, sunriseday=today, sunrisetime < earliest_time_blinds_up, sunrisetime >= datetime.now(), -> _open_blinds
    def test_open_blinds_sun_case8(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=7, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("off")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(hours=8, minutes=30), entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 09:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall9: on weekend, sunriseday=today, sunrisetime > earliest_time_blinds_up, sunrisetime < datetime.now(), -> _choose_open_blinds_method
    def test_open_blinds_sun_case9(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("off")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_sun
    # Fall10: on weekend, sunriseday=today, sunrisetime > earliest_time_blinds_up, sunrisetime >= datetime.now(), -> _open_blinds
    def test_open_blinds_sun_case10(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set sunrisetime
        blindscontrol.sunrise = mock.MagicMock(
            return_value=today + timedelta(hours=8, minutes=30))

        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("off")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("01:00:00")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_earliest_time_blinds_up").is_set_to("08:00:00")

        blindscontrol._open_blinds_sun(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(hours=9, minutes=30), entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 09:02:02", tz_offset=2)
    # _open_blinds_time
    # Fall1: timeup < datetime.now(); -> self._choose_open_blinds_method, today + timedelta(days=1, minutes=5)
    def test_open_blinds_time_case1(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set time to open blinds
        openblinds_on_time = today + \
            timedelta(hours=7, minutes=30, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_openblinds_on_time').is_set_to(openblinds_on_time, {
            "hour": openblinds_on_time.hour, "minute": openblinds_on_time.minute, "second": openblinds_on_time.second})

        blindscontrol._open_blinds_time(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(today + timedelta(days=1, minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_time
    # Fall2: timeup >= datetime.now(); -> self._open_blinds, timeup
    def test_open_blinds_time_case2(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)

        # set time to open blinds
        openblinds_on_time = today + \
            timedelta(hours=7, minutes=30, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_openblinds_on_time').is_set_to(openblinds_on_time, {
            "hour": openblinds_on_time.hour, "minute": openblinds_on_time.minute, "second": openblinds_on_time.second})

        blindscontrol._open_blinds_time(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(openblinds_on_time, entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_time
    # Fall3: timeup >= datetime.now() but its weekend!; -> self._open_blinds, timeup
    def test_open_blinds_time_case3(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        # set time for the test
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
                
        given_that.state_of(f"binary_sensor.workday_sensor").is_set_to("off")
        given_that.state_of(f"input_datetime.control_blinds_{cover}_offset_blinds_up_weekend").is_set_to("02:00:00")

        # set time to open blinds
        openblinds_on_time = today + \
            timedelta(hours=7, minutes=30, seconds=0)
        given_that.state_of(f'input_datetime.control_blinds_{cover}_openblinds_on_time').is_set_to(openblinds_on_time, {
            "hour": openblinds_on_time.hour, "minute": openblinds_on_time.minute, "second": openblinds_on_time.second})
                
        #set offset to 2 hours
        weekend_offset = timedelta(hours=2, minutes=0, seconds=0)
            
        #timeup + offset
        new_openblinds_on_time = openblinds_on_time + weekend_offset
        
        blindscontrol._open_blinds_time(entityid=cover)
        assert_that(blindscontrol) \
            .registered.run_at(new_openblinds_on_time, entityid=cover) \
            .with_callback(blindscontrol._open_blinds)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds
    # Fall1: current_position<100; -> cover/open_cover -> self._choose_open_blinds_method, datetime.now() + timedelta(minutes=5)
    def test__open_blinds_case1(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        blindscontrol._open_blinds({"entityid": cover})
        assert_that(
            'cover/open_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds
    # Fall2: current_position=100; -> self._choose_open_blinds_method, datetime.now() + timedelta(minutes=5)
    def test__open_blinds_case2(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        blindscontrol._open_blinds({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._choose_open_blinds_method)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_cooldown_
    # Fall1: current_position<100; -> cover/open_cover -> self._open_blinds_cooldown, datetime.now() + timedelta(minutes=5)
    def test__open_blinds_cooldown__case1(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        blindscontrol._open_blinds_cooldown_({"entityid": cover})
        assert_that(
            'cover/open_cover').was.called_with(entity_id=f"cover.{cover}")
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds_cooldown_
    # Fall2: current_position=100; -> self._open_blinds_cooldown, datetime.now() + timedelta(minutes=5)
    def test__open_blinds_cooldown__case2(self, given_that, blindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        cover = 'living_room'

        given_that.state_of(f"cover.{cover}").is_set_to(
            "open", {'friendly_name': f"{cover}", 'current_position': 100, 'value_id': cover})

        blindscontrol._open_blinds_cooldown_({"entityid": cover})
        assert_that(blindscontrol) \
            .registered.run_at(datetime.now() + timedelta(minutes=5), entityid=cover) \
            .with_callback(blindscontrol._open_blinds_cooldown)


class TestGlobalBlindsControl:
    @pytest.fixture
    @freeze_time("2019-10-16 00:02:02", tz_offset=2)
    def globalblindscontrol(self, given_that):
        globalblindscontrol = GlobalBlindsControl(
            None, GlobalBlindsControl.__name__, None, None, None, None, None)

        # set namespace
        globalblindscontrol.set_namespace(None)

        # passed args
        given_that.passed_arg('debug').is_set_to('True')

        globalblindscontrol.initialize()
        given_that.mock_functions_are_cleared()
        return globalblindscontrol

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _open_blinds
    def test__open_blinds(self, given_that, globalblindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        entity="input_boolean.control_blinds_open_all_blinds_global"

        globalblindscontrol._open_blinds(entity, None, "off", "on", 1)
        assert_that(
            'cover/open_cover').was.called_with(entity_id="all")
        assert_that(
            'input_boolean/turn_off').was.called_with(entity_id=entity)

    @freeze_time("2019-10-16 05:02:02", tz_offset=2)
    # _close_blinds
    def test__close_blinds(self, given_that, globalblindscontrol, assert_that, caplog):
        caplog.set_level(logging.DEBUG)
        entity="input_boolean.control_blinds_close_all_blinds_global"

        globalblindscontrol._close_blinds(entity, None, "off", "on", 1)
        assert_that(
            'cover/close_cover').was.called_with(entity_id="all")
        assert_that(
            'input_boolean/turn_off').was.called_with(entity_id=entity)
